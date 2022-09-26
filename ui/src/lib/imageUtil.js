
export async function loadImage(url) {
  return new Promise((res) => {
    const image = new Image();
    image.crossOrigin = 'Anonymous';
    image.src = url;
    image.onload = () => res(image);
  });
}

function color(type, hasAlpha){
  if(type == "transparent")
    return hasAlpha ? "rgba(0, 0, 0, 0.0)" : "rgba(255, 255, 255, 1.0)";
  return "rgba(0, 0, 0, 1.0)";
}

function createGradient(ctx, x1, y1, x2, y2, type1, type2, hasAlpha){
  let grd = ctx.createLinearGradient(x1, y1, x2, y2);
  grd.addColorStop(0, color(type2, hasAlpha));
  grd.addColorStop(1, color(type1, hasAlpha));
  return grd;
}

export async function drawGradientImage(which, hasAlpha, width, height){
  let canvas = document.createElement('canvas');
  let ctx = canvas.getContext('2d');
  canvas.width = width;
  canvas.height = height;
  let grds = [];
  if(which.indexOf("L") != -1)
    grds.push(createGradient(ctx, 0, 0, width/2, 0, "transparent", "opaque", hasAlpha));
  if(which.indexOf("R") != -1)
    grds.push(createGradient(ctx, width/2, 0, width, 0, "opaque", "transparent", hasAlpha));
  if(which.indexOf("U") != -1)
    grds.push(createGradient(ctx, 0, 0, 0, height/2, "transparent", "opaque", hasAlpha));
  if(which.indexOf("D") != -1)
    grds.push(createGradient(ctx, 0, height/2, 0, height, "opaque", "transparent", hasAlpha));
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if(!hasAlpha){
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  ctx.globalCompositeOperation = 'darken';
  grds.forEach(grd => {
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  });
  return canvas.toDataURL();
}