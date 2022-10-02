export function sleep(n){
  return new Promise(r => setTimeout(r, n));
}

export function shallowCopy(obj){
  return {...obj};
}