'use strict';
/* Test GA4 privacy gating and bilingual consent with no external dependencies. */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const js = fs.readFileSync('js/analytics.js','utf8');
const KEY='dkk-analytics-consent-v1';
const ID='G-HF95H4P9VP';

function element(tag){
  return {tag,children:[],attrs:{},listeners:{},dataset:{},hidden:false,
    append(...xs){this.children.push(...xs);},
    appendChild(x){this.children.push(x);return x;},
    setAttribute(k,v){this.attrs[k]=v;},
    addEventListener(k,fn){this.listeners[k]=fn;},
    focus(){}
  };
}

function load({lang='en',stored=null}={}){
  const storage=new Map();
  if(stored)storage.set(KEY,stored);
  const head=element('head'),body=element('body'),footer=element('footer');
  const script=element('script');script.dataset.measurementId=ID;
  const document={
    documentElement:{lang},head,body,
    createElement:element,
    querySelector(selector){
      if(selector==='script[data-dkk-analytics]')return script;
      if(selector==='.footer-bottom')return footer;
      return null;
    }
  };
  const window={dataLayer:undefined};
  const localStorage={
    getItem:k=>storage.get(k)||null,
    setItem:(k,v)=>storage.set(k,v)
  };
  vm.runInNewContext(js,{window,document,localStorage,Date,encodeURIComponent}, {filename:'js/analytics.js',timeout:3000});
  const banner=body.children[0];
  const actions=banner.children[3];
  return {storage,head,footer,banner,window,
    accept:()=>actions.children[0].listeners.click(),
    reject:()=>actions.children[1].listeners.click(),
    settings:()=>footer.children[0].listeners.click(),
    label:banner.children[0].textContent,
  };
}

let no=load();
assert.equal(no.head.children.length,0,'No GA before consent');
assert.equal(no.banner.hidden,false,'Banner shown to visitor without choice');
no.reject();
assert.equal(no.storage.get(KEY),'denied');
assert.equal(no.head.children.length,0,'Reject never loads Google');
assert.equal(no.banner.hidden,true);
no.settings();
assert.equal(no.banner.hidden,false,'Settings can reopen panel');
no.accept();
assert.equal(no.storage.get(KEY),'granted');
assert.equal(no.head.children.length,1,'Accept loads Google exactly once');
assert.equal(no.head.children[0].src,'https://www.googletagmanager.com/gtag/js?id='+ID);
assert.equal(no.window.dataLayer.some(row=>row[0]==='config' && row[1]===ID),true);
no.settings();no.reject();
assert.equal(no.window.dataLayer.some(row=>row[0]==='consent' && row[1]==='update' && row[2].analytics_storage==='denied'),true,'Revoking consent updates consent mode');
assert.equal(no.head.children.length,1,'Revocation does not add more tracking scripts');

let yes=load({stored:'granted'});
assert.equal(yes.banner.hidden,true);
assert.equal(yes.head.children.length,1,'Stored consent loads GA on next page');
yes.settings();yes.accept();
assert.equal(yes.head.children.length,1,'Duplicate script prevented');

let denied=load({stored:'denied'});
assert.equal(denied.banner.hidden,true);
assert.equal(denied.head.children.length,0);

let polish=load({lang:'pl'});
assert.equal(polish.label,'Prywatność i statystyki');
assert.equal(polish.head.children.length,0);

console.log('PASS: GA4 measurement ID, consent before loading, refusal, revocation, persistence and Polish UI');
