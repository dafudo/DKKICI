/* Digitally published editions are derived from the single publications JSON catalogue.
   New confirmed Google Play links need no separate shelf maintenance. */
(() => {
  'use strict';
  const shelf=document.querySelector('[data-google-shelf]');
  if(!shelf)return;
  const lang=document.documentElement.lang==='pl'?'pl':'en';
  const root=document.body.dataset.root||'../';
  const fallback=shelf.dataset.fallback||root+'assets/cover-support.svg';
  const clean=(u)=>{try{const x=new URL(u);return x.protocol==='https:'&&x.hostname==='play.google.com'&&x.pathname.startsWith('/store/books/')?x.href:null}catch{return null}};
  const titleOf=p=>p.titleShort?.[lang]||p.title?.[lang]||p.title?.en||'';
  function render(data){
    const entries=data
      .filter(p=>p&&p.status==='published'&&p.cover&&Array.isArray(p.links))
      .map(p=>({p,google:p.links.find(link=>link.label==='Google Play Books'&&clean(link.url))}))
      .filter(x=>x.google)
      .sort((a,b)=>(b.p.date||'').localeCompare(a.p.date||''))
      .slice(0,6);
    const fragment=document.createDocumentFragment();
    for(const {p,google} of entries){
      const card=document.createElement('a');card.className='gp-book';
      card.href=clean(google.url);card.target='_blank';card.rel='noopener noreferrer';
      const visual=document.createElement('div');visual.className='gp-book__visual';
      const img=document.createElement('img');img.loading='lazy';img.decoding='async';
      img.width=360;img.height=480;img.src=root+p.cover;
      img.alt=titleOf(p)+' — Google Play Books cover';
      img.addEventListener('error',()=>{img.src=fallback},{once:true});
      const arrow=document.createElement('span');arrow.textContent='↗';arrow.setAttribute('aria-hidden','true');
      visual.append(img,arrow);
      const label=document.createElement('strong');label.textContent=titleOf(p);
      const meta=document.createElement('small');meta.textContent='Google Play Books';
      card.append(visual,label,meta);fragment.append(card);
    }
    if(fragment.childNodes.length)shelf.replaceChildren(fragment);
    else shelf.textContent=lang==='pl'?'Brak potwierdzonych wydań w Google Play.':'No verified Google Play editions currently listed.';
  }
  fetch(root+'data/publications.json',{cache:'no-cache'})
    .then(r=>r.ok?r.json():Promise.reject(Error('Catalogue unavailable')))
    .then(data=>render(Array.isArray(data)?data:[]))
    .catch(()=>{shelf.textContent=lang==='pl'?'Nie udało się załadować wydań.':'Digital editions could not be loaded.';});
})();