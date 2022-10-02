import uuid
import threading, queue, json
import argparse, os, sys, glob, time, traceback
import PIL
import cv2
import torch
import accelerate
import torch.nn as nn
import numpy as np
import k_diffusion as K
from PIL import Image, ImageFilter, ImageOps, ImageChops

from modules.devices import torch_gc
from modules import random_utils, UserDatabase, ProcessOptions, shared, sd_models, misc, gfpgan_model
from modules.ProcessOptions import ProcessOptions, seed_to_int
from modules.shared import opts as globalOpts, cmd_opts
from modules.processing import StableDiffusionProcessing, Processed, StableDiffusionProcessingTxt2Img, StableDiffusionProcessingImg2Img, process_images
from modules.sd_samplers import samplers, samplers_for_img2img

memImage = {}
memMask = {}
allRequests = {}
workQueue = queue.Queue()

try:
    # this silences the annoying "Some weights of the model checkpoint were not used when initializing..." message at start.
    from transformers import logging
    logging.set_verbosity_error()
except Exception:
    pass

def getSamplerIndex(sampler, isImg2Img = False):
    available_samplers = samplers_for_img2img if isImg2Img else samplers
    print(f"available samplers: {[x.name for x in available_samplers]}")
    sampler_indices = [i for i,x in enumerate(available_samplers) if x.name == sampler]
    if len(sampler_indices) == 0:
        raise Exception("Unknown sampler: " + sampler)
    return sampler_indices[0]

def saveImage(image):
    filename = str(uuid.uuid4()) + ".png"
    image.save(os.path.join(shared.cmd_opts.image_path, filename))
    return filename
    
def saveVideo(images, frameRate, size):
    filename = str(uuid.uuid4()) + ".webm"
    out = cv2.VideoWriter(os.path.join(shared.cmd_opts.image_path, filename), cv2.VideoWriter_fourcc(*'VP80'), frameRate, size)
    for img in images:
        out.write(np.array(img)[:, :, ::-1])
    out.release()
    return filename


def start_worker():
    def process_interpolate(item):
        opt = item["opt"]
        firstStep = opt["steps"][0]
        
        firstStep["seed"] = seed_to_int(firstStep["seed"])
        p = StableDiffusionProcessingTxt2Img(
            sd_model=shared.sd_model,
            prompt=firstStep["prompt"],
            seed=firstStep["seed"],
            sampler_index=getSamplerIndex(opt["samplingMethod"]),
            batch_size=1,
            n_iter=1,
            steps=opt["samplingSteps"],
            cfg_scale=opt["classifierStrength"],
            width=opt["width"],
            height=opt["height"],
            tiling=opt["tiling"],
        )
        processed = process_images(p)
        shared.total_tqdm.clear()
        images = [processed.images[0]]
                
        prevStep = None
        for step in opt["steps"]:
            if not prevStep:
                prevStep = step
                continue
            if not step["seed"]:
                step["seed"] = prevStep["seed"]
            else:
                step["seed"] = seed_to_int(step["seed"])
            if not step["prompt"]:
                step["prompt"] = prevStep["prompt"]
            
            for i in range(1,opt["nbImages"]):
                a = i/(opt["nbImages"]-1)
                p = StableDiffusionProcessingTxt2Img(
                    sd_model=shared.sd_model,
                    outpath_samples=globalOpts.outdir_samples or globalOpts.outdir_txt2img_samples,
                    outpath_grids=globalOpts.outdir_grids or globalOpts.outdir_txt2img_grids,
                    prompt=prevStep["prompt"],
                    prompt2=step["prompt"],
                    prompt2_strength=a,
                    styles=[],
                    negative_prompt="",
                    seed=prevStep["seed"],
                    subseed=step["seed"],
                    subseed_strength=a,
                    seed_resize_from_h=0,
                    seed_resize_from_w=0,
                    sampler_index=getSamplerIndex(opt["samplingMethod"]),
                    batch_size=1,
                    n_iter=1,
                    steps=opt["samplingSteps"],
                    cfg_scale=opt["classifierStrength"],
                    width=opt["width"],
                    height=opt["height"],
                    restore_faces=False,
                    tiling=opt["tiling"],
                )
                processed = process_images(p)
                shared.total_tqdm.clear()
                images.append(processed.images[0])
            prevStep = step

        return saveVideo(images, opt.get("framesBySec",15), (p.width,p.height))
        
    def process_txt2img(item):
        opt = item["opt"]
        p = StableDiffusionProcessingTxt2Img(
            sd_model=shared.sd_model,
            outpath_samples=globalOpts.outdir_samples or globalOpts.outdir_txt2img_samples,
            outpath_grids=globalOpts.outdir_grids or globalOpts.outdir_txt2img_grids,
            prompt=opt.prompt,
            styles=[opt.prompt_style, opt.prompt_style2],
            negative_prompt=opt.negative_prompt,
            seed=opt.seed,
            subseed=opt.subseed,
            subseed_strength=opt.subseed_strength,
            seed_resize_from_h=opt.seed_resize_from_h,
            seed_resize_from_w=opt.seed_resize_from_w,
            sampler_index=getSamplerIndex(opt.sampler),
            batch_size=opt.batch_size,
            n_iter=opt.n_iter,
            steps=opt.steps,
            cfg_scale=opt.cfg_scale,
            width=opt.width,
            height=opt.height,
            restore_faces=opt.restore_faces,
            tiling=opt.tiling,
        )
        p.perlin_strength = opt.perlin_strength
        p.perlin_octave = opt.perlin_octave
        processed = process_images(p)
        shared.total_tqdm.clear()
        print(processed.js())
        print(processed.info)
        return [saveImage(img) for img in processed.images]
        
    def process_img2img(item, init_img, init_mask = None):
        opt = item["opt"]
        try:
            inpainting_fill = ['fill', 'original', 'latent noise', 'latent nothing'].index(opt.inpainting_fill)
        except:
            inpainting_fill = 0
        try:
            resize_mode = ["Just resize", "Crop and resize", "Resize and fill"].index(opt.resize_mode)
        except:
            resize_mode = 0
        
        if init_mask:
            if opt.use_alpha:
                image = init_img
                mask = init_mask
                alpha_mask = ImageOps.invert(image.split()[-1]).convert('L').point(lambda x: 255 if x > 0 else 0, mode='1')
                mask = ImageChops.lighter(alpha_mask, mask.convert('L')).convert('L')
                image = image.convert('RGB')
            else:
                image = init_img
                mask = init_mask
        else:
            image = init_img
            mask = None

        p = StableDiffusionProcessingImg2Img(
            sd_model=shared.sd_model,
            outpath_samples=globalOpts.outdir_samples or globalOpts.outdir_img2img_samples,
            outpath_grids=globalOpts.outdir_grids or globalOpts.outdir_img2img_grids,
            prompt=opt.prompt,
            negative_prompt=opt.negative_prompt,
            styles=[opt.prompt_style, opt.prompt_style2],
            seed=opt.seed,
            subseed=opt.subseed,
            subseed_strength=opt.subseed_strength,
            seed_resize_from_h=opt.seed_resize_from_h,
            seed_resize_from_w=opt.seed_resize_from_w,
            sampler_index=getSamplerIndex(opt.sampler, True),
            batch_size=opt.batch_size,
            n_iter=opt.n_iter,
            steps=opt.steps,
            cfg_scale=opt.cfg_scale,
            width=opt.width,
            height=opt.height,
            restore_faces=opt.restore_faces,
            tiling=opt.tiling,
            init_images=[image],
            mask=mask,
            mask_blur=opt.mask_blur,
            inpainting_fill=inpainting_fill,
            resize_mode=resize_mode,
            denoising_strength=opt.denoising_strength,
            inpaint_full_res=opt.inpaint_full_res,
            inpainting_mask_invert=0 if opt.inpaint_mask else 1,
        )
        processed = process_images(p)
        shared.total_tqdm.clear()
        print(processed.js())
        print(processed.info)
        return [saveImage(img) for img in processed.images]

    def process_face_correction(image):
        image = image.convert("RGB")
        corrected_img = modules.face_restoration.restore_faces(np.array(image, dtype=np.uint8))
        filename = str(uuid.uuid4()) + ".png"
        Image.fromarray(corrected_img).save(os.path.join(shared.cmd_opts.image_path, filename))
        return filename

    def process_interrogate(image):
        return shared.interrogator.interrogate(image)

    def worker():
        global workQueue, allRequests, memImage
        shared.sd_model = sd_models.load_model()
        while(True):
            print(f'Wait for item')
            itemId = workQueue.get()
            image = memImage.pop(itemId, None)
            mask = memMask.pop(itemId, None)
            item = allRequests[itemId]
            if(item["status"] == "cancelling"):
                item["status"] = "cancelled"
                workQueue.task_done()
                continue
            print(f'Working on {itemId} {item}')
            shared.state.job_id = itemId
            shared.state.interrupted = False
            shared.state.job_no = 0;
            try:
                item["status"] = "processing"
                images = None
                prompt = None
                video = None
                if item["action"] == "interrogate":
                    shared.state.job_count = 1;
                    item["prompt"] = [process_interrogate(image)]
                elif item["action"] == "faceCorrection":
                    shared.state.job_count = 1;
                    item["images"] = [process_face_correction(image)]
                elif item["action"] == "img2img":
                    shared.state.job_count = item["opt"].n_iter;
                    item["images"] = process_img2img(item, image, mask)
                elif item["action"] == "interpolate":
                    shared.state.job_count = 1+item["opt"]["nbImages"]*(len(item["opt"]["steps"])-1);
                    item["video"] = process_interpolate(item)
                else:
                    shared.state.job_count = item["opt"].n_iter;
                    item["images"] = process_txt2img(item)
                if(item["status"] == "cancelling"):
                    item["status"] = "cancelled"
                else:
                    item["status"] = "done"
            except Exception as e:
                print("****** ERROR ******")
                print(traceback.format_exc())
                item["status"] = "error"
                item["message"] = str(e)
            shared.state.job_id = None
            torch_gc()
            allRequests[item["id"]] = item
            
            print(f'Finished {item}')
            workQueue.task_done()
    
    threading.Thread(target=worker, daemon=True).start()

def add_request_to_queue(response, image = None, mask = None):
    global allRequests, workQueue, memImage, memMask
    id = response["id"]
    if image:
        memImage[id] = image
    if mask:
        memMask[id] = mask
    allRequests[id] = response
    workQueue.put(id)

def get_request(id):
    global allRequests
    request = allRequests.get(id)
    print(f"check job id: {id}")
    print(f"current job id: {shared.state.job_id}")
    if shared.state.job_id != id:
        return request
    request["n"] = shared.state.job_count
    request["i"] = shared.state.job_no
    request["smplr n"] = shared.state.sampling_steps
    request["smplr i"] = shared.state.sampling_step
    return request

def cancel_request(id):
    request = get_request(id)
    if request: #@@CROQ@@ check current status
        request["status"] = 'cancelling'
    if shared.state.job_id == id:
        shared.state.interrupted = True
    return request
    
start_worker()
