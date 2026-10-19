'use strict';
/* Dependency-free browser-language regression checks for GitHub Actions. */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const script = fs.readFileSync('js/language.js', 'utf8');

function visit({
  pathname='/', htmlLanguage='en', browserLanguages=['pl-PL'],
  preference=null, search='', hash='', origin='https://dkk.hqici.com'
}={}) {
  const values = new Map();
  if (preference) values.set('dkk-preferred-language', preference);
  const callbacks = {};
  let redirected=null;
  const location={
    pathname, origin, search, hash, href:origin+pathname+search+hash,
    replace(uri){redirected=uri;}
  };
  const document={
    documentElement:{lang:htmlLanguage},
    addEventListener(event,callback){callbacks[event]=callback;}
  };
  const window={
    location,
    localStorage:{
      getItem(key){return values.get(key)??null;},
      setItem(key,value){values.set(key,value);}
    }
  };
  vm.runInNewContext(script,{
    window,document,navigator:{languages:browserLanguages,language:browserLanguages[0]||'en'},
    URL
  },{filename:'js/language.js',timeout:3000});
  return {
    redirect:redirected,
    getPreference:()=>values.get('dkk-preferred-language')??null,
    manualSwitch(href,lang=null){
      const link={href:origin+href,getAttribute(name){return name==='lang'?lang:null;}};
      callbacks.click({target:{closest(selector){assert.equal(selector,'a.locale-link');return link;}}});
    }
  };
}

assert.equal(
  visit({pathname:'/',browserLanguages:['pl-PL','en-AU'],search:'?utm_source=linkedin',hash:'#work'}).redirect,
  'https://dkk.hqici.com/pl/?utm_source=linkedin#work',
  'Polish primary language redirects only on English homepage');
assert.equal(visit({pathname:'/index.html',browserLanguages:['pl']}).redirect,'https://dkk.hqici.com/pl/');
assert.equal(visit({pathname:'/DKKICI/',browserLanguages:['pl']}).redirect,'https://dkk.hqici.com/DKKICI/pl/');
assert.equal(visit({pathname:'/',browserLanguages:['en-AU','pl-PL']}).redirect,null,'Primary browser language wins');
assert.equal(visit({pathname:'/',browserLanguages:['de-DE','es-ES']}).redirect,null,'Other languages get English');
assert.equal(visit({pathname:'/',browserLanguages:['fr-FR'],preference:'pl'}).redirect,'https://dkk.hqici.com/pl/','Manual PL preference persists');
assert.equal(visit({pathname:'/',browserLanguages:['pl-PL'],preference:'en'}).redirect,null,'Manual EN preference persists');
assert.equal(visit({pathname:'/works/support-needs/',browserLanguages:['pl-PL']}).redirect,null,'Linked English publication unchanged');
assert.equal(visit({pathname:'/profile/',browserLanguages:['pl-PL']}).redirect,null,'Direct English profile unchanged');
assert.equal(visit({pathname:'/pl/',htmlLanguage:'pl',browserLanguages:['en-AU']}).redirect,null,'Direct Polish homepage unchanged');
assert.equal(visit({pathname:'/pl/publikacje/support-needs/',htmlLanguage:'pl',browserLanguages:['en-AU']}).redirect,null,'Polish deep links unchanged');
const fromPL=visit({pathname:'/pl/',htmlLanguage:'pl',browserLanguages:['pl-PL']});
fromPL.manualSwitch('/index.html','en');
assert.equal(fromPL.getPreference(),'en','EN choice saved on manual switch');
assert.equal(visit({pathname:'/',browserLanguages:['pl-PL'],preference:fromPL.getPreference()}).redirect,null);
const fromEN=visit({pathname:'/works/support-needs/',browserLanguages:['en-AU']});
fromEN.manualSwitch('/pl/publikacje/support-needs/','pl');
assert.equal(fromEN.getPreference(),'pl','PL choice saved on manual switch');
assert.equal(visit({pathname:'/',browserLanguages:['en-AU'],preference:fromEN.getPreference()}).redirect,'https://dkk.hqici.com/pl/');
const fromPlainLinks=visit({pathname:'/profile/',browserLanguages:['en-AU']});
fromPlainLinks.manualSwitch('/pl/profil/');
assert.equal(fromPlainLinks.getPreference(),'pl','Switch without lang attribute also works');
console.log('PASS: browser locale, preference, deep links, query/hash, legacy GitHub Pages path, and both manual switches');
