export function getDetailFromUrl(details, url){
  return details.find(d => d.image == url);
}

export function getAndlockDetail(details, url){
  let detail = details.find(d => d.image == url);
  if(!detail){
    console.log("I can't found the detail to update");
    return;
  }
  if(detail.status == "pending"){
    console.log("Image is already locked");
    return null;
  }
  detail.status = "pending";
  return detail;
}

export function unlockAndUpdateDetail(details, url, params, newUrl, status){
  let detail = details.find(d => d.image == url);
  if(!detail){
    console.log("I can't found the detail to update");
    return;
  }
  detail.status = status || "done";
  if(status == "error")
    return;
  detail.image = newUrl || detail.image;
  detail.params = params || detail.params;
  detail.nbChange = (detail.nbChange || 0) + 1;
  return details;
}