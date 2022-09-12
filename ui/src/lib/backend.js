const backendUrl = "http://127.0.0.1:5001";
  
function promiseOnAjaxReturn(xhr){
  return new Promise((res, rej) => {
    xhr.onreadystatechange = function() {
      if(xhr.readyState == 4){
        console.log(xhr.status);
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

export async function img2img(image, data){
  let formData = new FormData();
  formData.append("image", image);
  formData.append("data", JSON.stringify(data));
  const xhr = new XMLHttpRequest();
  xhr.open("POST", backendUrl+"/img2img");
  xhr.send(formData);
  return promiseOnAjaxReturn(xhr);
  
}

export async function txt2img(data){
  const xhr = new XMLHttpRequest();
  xhr.open("POST", backendUrl+"/txt2img");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify(data));
  return promiseOnAjaxReturn(xhr);
}

export async function checkResult(id){
  const xhr = new XMLHttpRequest();
  xhr.open("GET", backendUrl+"/"+id);
  xhr.send();
  let res = await promiseOnAjaxReturn(xhr);
  if(res.images)
    res.images = res.images.map(img => backendUrl+"/static/"+img);
  return res;
}

export function cancel(id){
  const xhr = new XMLHttpRequest();
  xhr.open("GET", backendUrl+"/cancel/"+id);
  xhr.send(); 
  // fire and forget
}
