/* Google Play shelf uses the same verified record source as the publication catalogue. */
(() => {
  'use strict';
  const shelf=document.querySelector('[data-google-shelf]');
  if(!shelf)return;
  const lang=document.documentElement.lang==='pl'?'pl':'en';
  const root=document.body.dataset.root||'../';
  fetch(root+'data/publications.json',{cache:'no-cache'})
    .then(r=>{if(!r.ok)throw new Error('Catalogue unavailable');return r.json()})
    .then(records=>{
      const books=(Array.isArray(records)?records:[]).filter(p=>p.status==='published'&&p.googlePlayId&&p.cover);
      const frag=document.createDocumentFragment();
      for(const p of books){
        const link=(p.links||[]).find(l=>l.label==='Google Play Books'&&typeof l.url==='string'&&/^https:\/\/play\.google\.com\//.test(l.url));
        if(!link)continue;
        const a=document.createElement('a');a.className='gp-book';
        a.href=link.url;a.target='_blank';a.rel='noopener noreferrer';
        const v=document.createElement('div');v.className='gp-book__visual';
        const img=document.createElement('img');img.loading='lazy';img.decoding='async';
        img.src=root+p.cover;img.alt=(p.title[lang]||p.title.en)+' — '+(lang==='pl'?'okładka':'cover');
        const arrow=document.createElement('span');arrow.textContent='↗';arrow.setAttribute('aria-hidden','true');
        v.append(img,arrow);
        const h=document.createElement('strong');h.textContent=p.titleShort?.[lang]||p.title?.[lang]||p.title?.en;
        const subtitle=document.createElement('small');subtitle.textContent='Google Play Books';
        a.append(v,h,subtitle);frag.append(a);
      }
      shelf.replaceChildren(frag);
    })
    .catch(()=>{shelf.textContent=lang==='pl'?'Nie udało się pobrać wydań.':'The editions could not be loaded.'});
})();