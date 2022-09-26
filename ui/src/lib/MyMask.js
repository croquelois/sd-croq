import {loadImage} from './ImageUtil.js';

export class MyMask {
  constructor(w,h){
    let canvas = this.canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    this.ctx = canvas.getContext('2d');
    this.clear();
    this.img = null;
  }
  async prepareImg(){
    this.img = await loadImage(this.canvas.toDataURL());
  }
  drawImgInto(ctx){
    if(this.img)
      ctx.drawImage(this.img, 0, 0);
  }
  getMaskImage(left, top, width, height, alphaToApply){
    let imgData = this.ctx.getImageData(left, top, width, height);
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    canvas.width = width;
    canvas.height = height;
    for(let x=0;x<width;x++){
      for(let y=0;y<height;y++){
        let off = (y*width + x)*4 + 3; // alpha
        // 255 mean opaque, 0 mean transparent
        let alpha = imgData.data[off];
        alphaToApply[off] *= (1-alpha/255);
        imgData.data[off-3] = alpha;
        imgData.data[off-2] = alpha;
        imgData.data[off-1] = alpha;
        imgData.data[off] = 255;
      }
    }
    ctx.putImageData(imgData, 0, 0);
    return new Promise(res => canvas.toBlob(res));
  }
  clear(){
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }
  draw(x,y,r,color){
    let ctx = this.ctx;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, 2 * Math.PI, false);
    ctx.fillStyle = color || "white";
    ctx.fill();
  }
}