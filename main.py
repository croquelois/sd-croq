import uuid
import jsonpickle, json
from PIL import Image
from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
import os, shutil

from modules.worker import add_request_to_queue, get_request, cancel_request
from modules.ProcessOptions import ProcessOptions
from modules import UserDatabase
from modules import sd_models, shared

# nvidia-smi --query-gpu=timestamp,name,pci.bus_id,driver_version,pstate,pcie.link.gen.max,pcie.link.gen.current,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv -l 5

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

## PROCESSING

@app.route('/txt2img', methods=['POST'])
@cross_origin()
def txt2img():
    opt = ProcessOptions(request.json)
    response = {'action': 'txt2img', 'status': 'pending', 'i': 0, 'nb': opt.n_iter*(1+opt.nbLoopback), 'id': str(uuid.uuid4()), 'opt': opt};
    add_request_to_queue(response)
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

@app.route('/img2img', methods=['POST'])
@cross_origin()
def img2img():
    mask = request.files.get('mask', None)
    if mask:
        mask = Image.open(mask)
        mask.load()
        mask.save("debugSaveMaskImage.png");
    image = Image.open(request.files['image'])
    image.load()
    image.save("debugSaveInputImage.png");
    opt = ProcessOptions(json.loads(request.form['data']))
    response = {'action': 'img2img', 'status': 'pending', 'i': 0, 'nb': opt.n_iter*(1+opt.nbLoopback), 'id': str(uuid.uuid4()), 'opt': opt};
    add_request_to_queue(response, image, mask)
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")
    
@app.route('/faceCorrection', methods=['POST'])
@cross_origin()
def faceCorrection():
    image = Image.open(request.files['image'])
    image.load()
    response = {'action': 'faceCorrection', 'status': 'pending', 'id': str(uuid.uuid4())};
    add_request_to_queue(response, image)
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

@app.route('/upscale', methods=['POST'])
@cross_origin()
def upscale():
    image = Image.open(request.files['image'])
    image.load()
    opt = json.loads(request.form.get('data',"{}"))
    response = {'action': 'upscale', 'status': 'pending', 'id': str(uuid.uuid4()), 'opt': opt};
    add_request_to_queue(response, image)
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")
    
@app.route('/interrogate', methods=['POST'])
@cross_origin()
def interrogate():
    image = Image.open(request.files['image'])
    image.load()
    response = {'action': 'interrogate', 'status': 'pending', 'id': str(uuid.uuid4())};
    add_request_to_queue(response, image)
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

@app.route('/interpolate', methods=['POST'])
@cross_origin()
def interpolate():
    opt = request.json
    print(jsonpickle.encode(opt))
    nb_img = opt["nbImages"]
    nb_keys = len(opt["steps"])
    response = {'action': 'interpolate', 'status': 'pending', 'i': 0, 'nb': (1+nb_img*(nb_keys-1)), 'id': str(uuid.uuid4()), 'opt': opt};
    add_request_to_queue(response)
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

## QUEUE

@app.route('/<id>')
@cross_origin()
def check(id):
    response = get_request(id)
    if response == None:
        response = {'status': 'error', 'message': 'unknown id request'}
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

@app.route('/cancel/<id>')
@cross_origin()
def cancel(id):
    response = cancel_request(id)
    if response == None:
        response = {'status': 'error', 'message': 'unknown id request'}
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

## USER DATABASE

@app.route('/db/<user>', methods=['POST'])
@cross_origin()
def dbAppend(user):
    data = UserDatabase.load(user)
    data.append(request.json)
    UserDatabase.save(user, data)
    return Response(response=jsonpickle.encode({'status': 'ok', 'data': data}), status=200, mimetype="application/json")

@app.route('/db/<user>/<url>', methods=['POST'])
@cross_origin()
def dbUpdate(user, url):
    data = UserDatabase.load(user)
    for i,d in enumerate(data):
        if d["url"] == url:
            data[i] = request.json
    UserDatabase.save(user, data)
    return Response(response=jsonpickle.encode({'status': 'ok', 'data': data}), status=200, mimetype="application/json")

@app.route('/db/<user>/<url>', methods=['DELETE'])
@cross_origin()
def dbDelete(user, url):
    data = [h for h in UserDatabase.load(user) if h["url"] != url]
    UserDatabase.save(user, data)
    return Response(response=jsonpickle.encode({'status': 'ok', 'data': data}), status=200, mimetype="application/json")

@app.route('/db/<user>')
@cross_origin()
def dbRead(user):
    data = UserDatabase.load(user)
    return Response(response=jsonpickle.encode({'status': 'ok', 'data': data}), status=200, mimetype="application/json")

@app.route('/admin/clean')
@cross_origin()
def adminClean():
    fileToKeep = []
    users = UserDatabase.listUsers()
    for user in users:
        data = UserDatabase.load(user)
        fileToKeep = fileToKeep + [h["url"] for h in data]
    #os.makedirs("backup", exist_ok=True)
    #for file in fileToKeep:
    #    shutil.copy("static/"+file,"backup/"+file);
    fileToKeep = set(fileToKeep)
    for file in os.listdir("static"):
        if not file in fileToKeep:
            os.remove("static/" + file)
    return Response(response=jsonpickle.encode({'status': 'ok'}), status=200, mimetype="application/json")

@app.route('/admin/models')
@cross_origin()
def models():
    titles = [info.title for info in sd_models.checkpoints_list.values()]
    model = shared.opts.sd_model_checkpoint
    return Response(response=jsonpickle.encode({'status': 'ok', 'list': titles, 'model': model}), status=200, mimetype="application/json")

@app.route('/admin/models', methods=['POST'])
@cross_origin()
def setModel():
    shared.opts.sd_model_checkpoint = request.json["name"]
    sd_models.reload_model_weights(shared.sd_model)
    return Response(response=jsonpickle.encode({'status': 'ok'}), status=200, mimetype="application/json")

app.run(host="127.0.0.1", port=5001)