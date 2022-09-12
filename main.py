# nvidia-smi --query-gpu=timestamp,name,pci.bus_id,driver_version,pstate,pcie.link.gen.max,pcie.link.gen.current,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv -l 5
import uuid, random
import threading, queue
import argparse, os, sys, glob, time, traceback
import PIL
import torch
import accelerate
import json, jsonpickle
import torch.nn as nn
import numpy as np
import k_diffusion as K
from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
from PIL import Image
from omegaconf import OmegaConf
from itertools import islice
from einops import rearrange, repeat
from torchvision.utils import make_grid
from torch import autocast
from contextlib import nullcontext
from pytorch_lightning import seed_everything
from ldm.util import instantiate_from_config
from ldm.models.diffusion.ddim import DDIMSampler
from ldm.models.diffusion.plms import PLMSSampler

SD_REPO_PATH = "../../sd-webui/stable-diffusion-webui"
IMG_PATH = "static"

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

memImage = {};
allRequests = {};
workQueue = queue.Queue()

def torch_gc():
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

class CFGDenoiser(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.inner_model = model

    def forward(self, x, sigma, uncond, cond, cond_scale):
        x_in = torch.cat([x] * 2)
        sigma_in = torch.cat([sigma] * 2)
        cond_in = torch.cat([uncond, cond])
        uncond, cond = self.inner_model(x_in, sigma_in, cond=cond_in).chunk(2)
        return uncond + (cond - uncond) * cond_scale


class KDiffusionSampler:
    def __init__(self, m, sampler):
        self.model = m
        self.model_wrap = K.external.CompVisDenoiser(m)
        self.schedule = sampler
    def get_sampler_name(self):
        return self.schedule
    def sample(self, S, conditioning, batch_size, shape, verbose, unconditional_guidance_scale, unconditional_conditioning, eta, x_T):
        sigmas = self.model_wrap.get_sigmas(S)
        x = x_T * sigmas[0]
        model_wrap_cfg = CFGDenoiser(self.model_wrap)

        samples_ddim = K.sampling.__dict__[f'sample_{self.schedule}'](model_wrap_cfg, x, sigmas, extra_args={'cond': conditioning, 'uncond': unconditional_conditioning, 'cond_scale': unconditional_guidance_scale}, disable=False)

        return samples_ddim, None

def load_model_from_config(config, ckpt, verbose=False):
    print(f"Loading model from {ckpt}")
    pl_sd = torch.load(ckpt, map_location="cpu")
    if "global_step" in pl_sd:
        print(f"Global Step: {pl_sd['global_step']}")
    sd = pl_sd["state_dict"]
    model = instantiate_from_config(config.model)
    m, u = model.load_state_dict(sd, strict=False)
    if len(m) > 0 and verbose:
        print("missing keys:")
        print(m)
    if len(u) > 0 and verbose:
        print("unexpected keys:")
        print(u)

    model.cuda()
    model.eval()
    return model

def seed_to_int(s):
    print(s)
    if type(s) is int:
        print("int")
        return s
    if s is None or s == '':
        print("null")
        return random.randint(0, 2**32 - 1)
    n = abs(int(s) if s.isdigit() else random.Random(s).randint(0, 2**32 - 1))
    while n >= 2**32:
        n = n >> 32
    return n

class ProcessOptions:
    def __init__(self):
        self.prompt = ""
        self.sampler = "DDIM"
        self.nbImages = 1
        self.height = 512
        self.width = 512
        self.samplingSteps = 50
        self.classifierStrength = 7.5
        self.seed = 42
        self.denoiserStrength = 0.75
        self.denoiserStrengthFactor = 0.5
        self.nbLoopback = 0
        self.saveLoopback = False

def start_worker():
    accelerator = accelerate.Accelerator()
    device = accelerator.device
    seed_everything(42)
    seeds = torch.randint(-2 ** 63, 2 ** 63 - 1, [accelerator.num_processes])
    torch.manual_seed(seeds[accelerator.process_index].item())
    config = OmegaConf.load(SD_REPO_PATH+"/configs/stable-diffusion/v1-inference.yaml")
    model = load_model_from_config(config, SD_REPO_PATH+"/models/ldm/stable-diffusion-v1/model.ckpt")
    model = model.half()
    precision_scope = autocast
    
    def process_image(item, init_img):
        nonlocal model
        if not model: #Lazy init
            model = load_model_from_config(config, SD_REPO_PATH+"/models/ldm/stable-diffusion-v1/model.ckpt")
            model = model.half()
        opt = item["opt"]
        
        if opt.sampler == 'DDIM':
            sampler = DDIMSampler(model)
        elif opt.sampler == 'DPM2 a':
            sampler = KDiffusionSampler(model,'dpm_2_ancestral')
        elif opt.sampler == 'DPM2':
            sampler = KDiffusionSampler(model,'dpm_2')
        elif opt.sampler == 'Euler a':
            sampler = KDiffusionSampler(model,'euler_ancestral')
        elif opt.sampler == 'Euler':
            sampler = KDiffusionSampler(model,'euler')
        elif opt.sampler == 'Heun':
            sampler = KDiffusionSampler(model,'heun')
        elif opt.sampler == 'LMS':
            sampler = KDiffusionSampler(model,'lms')
        else:
            raise Exception("Unknown sampler: " + opt.sampler)
            
        shape = [4, opt.height // 8, opt.width // 8]
        def func_init():
            if not init_img:
                return None
            image = init_img.copy().convert("RGB")
            image = image.resize((opt.width, opt.height), resample=PIL.Image.LANCZOS)
            image = np.array(image).astype(np.float32) / 255.0
            image = image[None].transpose(0, 3, 1, 2)
            image = torch.from_numpy(image)
            image = 2.*image - 1.
            image = image.to(device)
            image = repeat(image, '1 ... -> b ...', b=1)
            init_latent = model.get_first_stage_encoding(model.encode_first_stage(image))
            return init_latent
            
        def func_sample(x0, x, c, uc, nLoopback):
            if not init_img and nLoopback > 0:
                nLoopback = nLoopback - 1
            t_enc = int(opt.denoiserStrength * opt.samplingSteps * (opt.denoiserStrengthFactor ** nLoopback))
            if x0 == None:
                samples_ddim, _ = sampler.sample(S=opt.samplingSteps, 
                                            conditioning=c, 
                                            batch_size=1, 
                                            shape=shape, 
                                            verbose=False, 
                                            unconditional_guidance_scale=opt.classifierStrength, 
                                            unconditional_conditioning=uc,
                                            eta=0.0,
                                            x_T=x)
                return samples_ddim
            if opt.sampler == "DDIM":
                sampler.make_schedule(ddim_num_steps=opt.samplingSteps, ddim_eta=0.0, verbose=False)
                z_enc = sampler.stochastic_encode(x0, torch.tensor([t_enc]).to(device))
                return sampler.decode(z_enc, c, t_enc,
                                              unconditional_guidance_scale=opt.classifierStrength,
                                              unconditional_conditioning=uc, x0=x0)
            sigmas = sampler.model_wrap.get_sigmas(opt.samplingSteps)
            noise = x * sigmas[opt.samplingSteps - t_enc - 1]
            xi = x0 + noise
            sigma_sched = sigmas[opt.samplingSteps - t_enc - 1:]
            model_wrap_cfg = CFGMaskedDenoiser(sampler.model_wrap)
            samples_ddim = K.sampling.__dict__[f'sample_{sampler.get_sampler_name()}'](model_wrap_cfg, xi, sigma_sched, 
                    extra_args={'cond': c, 'uncond': uc, 'cond_scale': opt.classifierStrength, 'x0': x0, 'xi': xi},
                    disable=False)
            
        def create_random_tensors(w, h, n, n2):
            torch.manual_seed(opt.seed + n + n2*1000)
            return torch.randn([1, 4, h // 8, w // 8], device=device)
        
        def save_sample(samples_ddim):
            x_samples = model.decode_first_stage(samples_ddim)
            x_sample = x_samples[0]
            x_sample = torch.clamp((x_sample + 1.0) / 2.0, min=0.0, max=1.0)
            x_sample = accelerator.gather(x_sample)
            x_sample = 255. * rearrange(x_sample.cpu().numpy(), 'c h w -> h w c')
            filename = str(uuid.uuid4()) + ".png"
            Image.fromarray(x_sample.astype(np.uint8)).save(os.path.join(IMG_PATH, filename))
            return filename
            
        torch_gc()
        images = []
        with torch.no_grad(), precision_scope("cuda"), model.ema_scope():
            for n in range(opt.nbImages):
                x0 = func_init()
                for nLoopback in range(opt.nbLoopback+1):
                    if(item["status"] == "cancelling"):
                        return images
                    torch_gc()
                    uc = model.get_learned_conditioning([""])
                    c = model.get_learned_conditioning([opt.prompt])
                    x = create_random_tensors(opt.width, opt.height, n, nLoopback)
                    samples_ddim = func_sample(x0, x, c, uc, nLoopback)
                    x0 = samples_ddim
                    item["i"] = n*(opt.nbLoopback+1)+nLoopback+1
                    if opt.saveLoopback or nLoopback == opt.nbLoopback:
                        images.append(save_sample(samples_ddim))
        torch_gc()
        return images
    
    def worker():
        global workQueue, allRequests, memImage
        while(True):
            print(f'Wait for item')
            itemId = workQueue.get()
            image = memImage.pop(itemId, None)
            item = allRequests[itemId]
            if(item["status"] == "cancelling"):
                item["status"] = "cancelled"
                workQueue.task_done()
                continue
            print(f'Working on {id} {item}')
            try:
                item["status"] = "processing"
                images = process_image(item, image)
                item["images"] = images
                if(item["status"] == "cancelling"):
                    item["status"] = "cancelled"
                else:
                    item["status"] = "done"
            except Exception as e:
                print("****** ERROR ******")
                print(traceback.format_exc())
                item["status"] = "error"
                item["message"] = str(e)
            torch_gc()
            allRequests[item["id"]] = item
            
            print(f'Finished {item}')
            workQueue.task_done()
    
    threading.Thread(target=worker, daemon=True).start()

def add_request_to_queue(response):
    global allRequests, workQueue
    id = response["id"]
    allRequests[id] = response
    workQueue.put(id)

start_worker()

@app.route('/<id>')
@cross_origin()
def check(id):
    global allRequests
    response = allRequests.get(id)
    if response == None:
        response = {'status': 'error', 'message': 'unknown id request'}
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

@app.route('/cancel/<id>')
@cross_origin()
def cancel(id):
    global allRequests
    print(f"cancel request received for {id}");
    response = allRequests.get(id)
    if response == None:
        response = {'status': 'error', 'message': 'unknown id request'}
    else:
        response["status"] = 'cancelling'
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")
    
@app.route('/txt2img', methods=['POST'])
@cross_origin()
def txt2img():
    print("txt2img request received")
    
    content = request.json
    opt = ProcessOptions()
    opt.prompt = content.get("prompt", "")
    opt.width = content.get("width", 512)
    opt.height = content.get("height", 512)
    opt.classifierStrength = content.get("classifierStrength", 7.5)
    opt.samplingSteps = content.get("samplingSteps", 50)
    opt.nbImages = content.get("nbImages", 1)
    opt.seed = seed_to_int(content.get("seed"))
    opt.sampler = content.get("sampler", "DDIM")
    opt.denoiserStrength = content.get("denoiserStrength", 0.75)
    opt.denoiserStrengthFactor = content.get("denoiserStrengthFactor", 0.5)
    opt.nbLoopback = content.get("nbLoopback", 0)
    opt.saveLoopback = content.get("saveLoopback", False)
    
    response = {'status': 'pending', 'i': 0, 'nb': opt.nbImages*(1+opt.nbLoopback), 'id': str(uuid.uuid4()), 'opt': opt};
    add_request_to_queue(response)
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

@app.route('/img2img', methods=['POST'])
@cross_origin()
def img2img():
    global memImage
    print("img2img request received")
    
    image = request.files['image']
    image = Image.open(image)
    image.load()
    content = json.loads(request.form['data'])
    opt = ProcessOptions()
    opt.prompt = content.get("prompt", "")
    opt.width = content.get("width", 512)
    opt.height = content.get("height", 512)
    opt.classifierStrength = content.get("classifierStrength", 7.5)
    opt.samplingSteps = content.get("samplingSteps", 50)
    opt.nbImages = content.get("nbImages", 1)
    opt.seed = seed_to_int(content.get("seed"))
    opt.sampler = content.get("sampler", "DDIM")
    opt.denoiserStrength = content.get("denoiserStrength", 0.75)
    opt.denoiserStrengthFactor = content.get("denoiserStrengthFactor", 0.5)
    opt.nbLoopback = content.get("nbLoopback", 0)
    opt.saveLoopback = content.get("saveLoopback", False)
    
    response = {'status': 'pending', 'i': 0, 'nb': opt.nbImages*(1+opt.nbLoopback), 'id': str(uuid.uuid4()), 'opt': opt};
    memImage[response["id"]] = image
    add_request_to_queue(response)
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

@app.route('/api/test', methods=['POST'])
@cross_origin()
def test():
    nparr = np.fromstring(request.data, np.uint8)
    image = Image.open(nparr)
    response = {'message': 'image received'}
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

app.run(host="127.0.0.1", port=5001)
#workQueue.join()