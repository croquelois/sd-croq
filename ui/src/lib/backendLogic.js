import {txt2img, img2img, checkResult, cancel} from './backend.js';
import {sleep} from './utils.js'

let cancelling = false;

export async function generate(opt, image, feedback){
  console.log("generate", opt);
  let res;
  if(image)
    res = await img2img(image, opt);
  else
    res = await txt2img(opt);
  if(res.status == "error"){
    console.log(res);
    return res;
  }
  let id = res.id;
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

export async function cancelRequest(){
  cancelling = true;
  cancel();
}