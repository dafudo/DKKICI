/* Number-sensitive labels for publication counters in the browser and tests. */
(function (root) {
  'use strict';
  const rules = new Intl.PluralRules('pl');
  function publicationWord(n,language) {
    n=Number(n);
    if(!Number.isInteger(n)||n<0) throw new RangeError('Invalid publication count');
    if(language!=='pl') return n===1?'publication':'publications';
    const form=rules.select(n);
    return form==='one'?'publikacja':form==='few'?'publikacje':'publikacji';
  }
  if(typeof module!=='undefined'&&module.exports)module.exports=publicationWord;
  root.DKKPublicationWord=publicationWord;
})(typeof globalThis!=='undefined'?globalThis:this);
