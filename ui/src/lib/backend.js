const backendUrl = "http://127.0.0.1:5001";
  
export function addBackendUrl(url){
  return backendUrl+"/static/"+url;
}

export function removeBackendUrl(url){
  return url.split("/").slice(-1)[0];
}

function promiseOnAjaxReturn(xhr){
  return new Promise((res, rej) => {
    xhr.onreadystatechange = function() {
      if(xhr.readyState == 4){
        if(xhr.status == 0)
          return res({status: "error", message:"unable to contact the backend"});
        if(xhr.status == 500) {
          console.log(xhr.responseText);
          return res({status: "error", message:"backend crashed"});
        }
        let json;
        try {
          json = JSON.parse(xhr.responseText);
        } catch(err) {
          console.log(xhr.responseText);
          return res({status: "error", message:"can't parse backend response"});
        }
        return res(json);
      }
    };
  });
}

function addBackendUrlToResponse(res){
  if(res.images)
    res.images = res.images.map(addBackendUrl);
  if(res.video)
    res.video = addBackendUrl(res.video);
  return res;
}

function addBackendUrlToHistory(res){
  if(res.data)
    res.data.forEach(h => h.url = addBackendUrl(h.url));
  return res;
}

export async function img2img(data, image, mask){
  let formData = new FormData();
  formData.append("image", image);
  if(mask)
    formData.append("mask", mask);
  formData.append("data", JSON.stringify(data));
  const xhr = new XMLHttpRequest();
  xhr.open("POST", backendUrl+"/img2img");
  xhr.send(formData);
  return addBackendUrlToResponse(await promiseOnAjaxReturn(xhr));
  
}

export async function txt2img(data){
  const xhr = new XMLHttpRequest();
  xhr.open("POST", backendUrl+"/txt2img");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify(data));
  return addBackendUrlToResponse(await promiseOnAjaxReturn(xhr));
}

export async function interpolate(data){
  const xhr = new XMLHttpRequest();
  xhr.open("POST", backendUrl+"/interpolate");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify(data));
  return addBackendUrlToResponse(await promiseOnAjaxReturn(xhr));
}

export async function simpleImagePostRequest(path, image){
  let formData = new FormData();
  formData.append("image", image);
  const xhr = new XMLHttpRequest();
  xhr.open("POST", backendUrl+"/"+path);
  xhr.send(formData);
  return addBackendUrlToResponse(await promiseOnAjaxReturn(xhr));
}

export async function faceCorrection(image){
  return await simpleImagePostRequest("faceCorrection", image);
}

export async function upscale(image){
  return await simpleImagePostRequest("upscale", image);
}

export async function interrogate(image){
  return await simpleImagePostRequest("interrogate", image);
}

export async function checkResult(id){
  const xhr = new XMLHttpRequest();
  xhr.open("GET", backendUrl+"/"+id);
  xhr.send();
  return addBackendUrlToResponse(await promiseOnAjaxReturn(xhr));
}

export function cancel(id){
  const xhr = new XMLHttpRequest();
  xhr.open("GET", backendUrl+"/cancel/"+id);
  xhr.send(); 
  // fire and forget
}

export async function dbUserRead(user){
  const xhr = new XMLHttpRequest();
  xhr.open("GET", backendUrl+"/db/"+user);
  xhr.send();
  return addBackendUrlToHistory(await promiseOnAjaxReturn(xhr));
}

export async function dbUserDeleteOne(user, url){
  const xhr = new XMLHttpRequest();
  xhr.open("DELETE", backendUrl+"/db/"+user+"/"+removeBackendUrl(url));
  xhr.send();
  return addBackendUrlToHistory(await promiseOnAjaxReturn(xhr));
}

export async function dbUserAppend(user, data){
  const xhr = new XMLHttpRequest();
  data.url = removeBackendUrl(data.url);
  xhr.open("POST", backendUrl+"/db/"+user);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify(data));
  return addBackendUrlToHistory(await promiseOnAjaxReturn(xhr));
}

export async function dbUserUpdate(user, data){
  const xhr = new XMLHttpRequest();
  data.url = removeBackendUrl(data.url);
  xhr.open("POST", backendUrl+"/db/"+user+"/"+data.url);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify(data));
  return addBackendUrlToHistory(await promiseOnAjaxReturn(xhr));
}