import {txt2img, img2img, checkResult, faceCorrection, upscale, interrogate, interpolate, cancel} from './backend.js';
import {sleep} from './utils.js'

let cancelling = false;
let pendingReqId = null;

async function activeWaitLoop(id, feedback){
  console.log("request id", id);
  while(!cancelling){
    console.log("checking result", id);
    let res = await checkResult(id);
    feedback(res);
    console.log("checkResult", id, res);
    if(res.status == "done"){
      return res;
    }
    if(res.status == "error"){
      console.log(res);
      return res;
    }
    await sleep(5000);
  }
  cancelling = false;
  return {cancelled: true};
}

export async function generate(opt, image, mask, feedback){
  console.log("generate", opt);
  let res;
  pendingReqId = null; //@@CROQ@@ the request id would be better one step upper
  if(image)
    res = await img2img(opt, image, mask);
  else
    res = await txt2img(opt);
  if(res.status == "error"){
    console.log(res);
    return res;
  }
  pendingReqId = res.id;
  return await activeWaitLoop(res.id, feedback);
}

export async function interpolateRequest(opt, feedback){
  console.log("interpolate", opt);
  let res = await interpolate(opt);
  if(res.status == "error"){
    console.log(res);
    return res;
  }
  return await activeWaitLoop(res.id, feedback);
}

export async function faceCorrectionRequest(image, feedback){
  console.log("faceCorrectionRequest");
  let res = await faceCorrection(image);
  if(res.status == "error"){
    console.log(res);
    return res;
  }
  return await activeWaitLoop(res.id, feedback);
}

export async function upscaleRequest(image, feedback){
  console.log("upscaleRequest");
  let res = await upscale(image);
  if(res.status == "error"){
    console.log(res);
    return res;
  }
  return await activeWaitLoop(res.id, feedback);
}

export async function interrogateRequest(image, feedback){
  console.log("interrogateRequest");
  let res = await interrogate(image);
  if(res.status == "error"){
    console.log(res);
    return res;
  }
  return await activeWaitLoop(res.id, feedback);
}

export async function cancelRequest(){
  cancelling = true;
  cancel(pendingReqId);
}