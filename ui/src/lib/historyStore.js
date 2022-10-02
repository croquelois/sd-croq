import { writable } from 'svelte/store';
import {dbUserRead, dbUserDeleteOne, dbUserAppend, dbUserUpdate} from './backend.js'

function createStore(){
  let {set, subscribe} = writable([]);
  let data = [];
  let user = "default";
  
  function setUser(newUser){
    user = (newUser || "default");
    refresh();
  }
  async function append(p, overrideUser){
    let res = await dbUserAppend(overrideUser || user, p);
    if(res.status == "error")
      return console.log(res);
    set(res.data);
  }
  async function transfert(p, newUser){
    let res = await dbUserAppend(newUser, p);
    if(res.status == "error")
      return console.log(res);
    res = await dbUserDeleteOne(user, p.url);
    if(res.status == "error")
      return console.log(res);
    set(res.data);
  }
  async function update(p){
    let res = await dbUserUpdate(user, p);
    if(res.status == "error")
      return console.log(res);
    set(res.data);
  }
  async function deleteOne(url){
    let res = await dbUserDeleteOne(user, url);
    if(res.status == "error")
      return console.log(res);
    set(res.data);
  }
  async function refresh(){
    let res = await dbUserRead(user);
    if(res.status == "error")
      return console.log(res);
    set(res.data);
  }
  return {append, deleteOne, refresh, subscribe, setUser, transfert, update};
}
export let historyStore = createStore();