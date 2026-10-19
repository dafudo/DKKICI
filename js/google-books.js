/* Digital edition cards follow each publication's verified source links.
   Supports Apple Books, Google Play Books and Amazon without placeholder links. */
(() => {
  'use strict';
  const shelf=document.querySelector('[data-google-shelf]');
  if(!shelf)return;
  const lang=document.documentElement.lang==='pl'?'pl':'en';
  const root=document.body.dataset.root||'../';
  const fallback=shelf.dataset.fallback||root+'assets/cover-support.svg';
  const supported=['Apple Books','Google Play Books','Amazon'];
  const urlOf=(link)=>{
    try{
      const url=new URL(link.url);
      if(url.protocol!=='https:')return null;
      const hosts={
        'Apple Books':h=>h==='books.apple.com',
        'Google Play Books':h=>h==='play.google.com',
        'Amazon':h=>h==='amazon.com'||h.endsWith('.amazon.com')||/^amazon\.[a-z.]+$/.test(h)||/^www\.amazon\.[a-z.]+$/.test(h)
      };
      return hosts[link.label]?.(url.hostname.toLowerCase())?url.href:null;
    }catch{return null;}
  };
  const titleOf=p=>p.titleShort?.[lang]||p.title?.[lang]||p.title?.en||'';
  const entriesOf=data=>data.filter(p=>p?.status==='published'&&p.cover&&Array.isArray(p.links))
    .map(p=>{
      const sources=p.links.filter(v=>supported.includes(v.label)&&urlOf(v));
      const chosen=supported.map(s=>sources.find(v=>v.label===s)).find(Boolean);
      return {p,chosen,sources};
    }).filter(x=>x.chosen)
    .sort((a,b)=>(b.p.date||'').localeCompare(a.p.date||'')).slice(0,8);
  function render(data){
    const fragment=document.createDocumentFragment();
    for(const {p,chosen,sources} of entriesOf(data)){
      const card=document.createElement('a');card.className='gp-book';
      card.href=urlOf(chosen);card.target='_blank';card.rel='noopener noreferrer';
      const visual=document.createElement('div');visual.className='gp-book__visual';
      const img=document.createElement('img');
      img.loading='lazy';img.decoding='async';img.width=360;img.height=480;
      img.src=root+p.cover;img.alt=titleOf(p)+' — cover';
      img.addEventListener('error',()=>{img.src=fallback},{once:true});
      const arrow=document.createElement('span');arrow.textContent='↗';arrow.setAttribute('aria-hidden','true');
      visual.append(img,arrow);
      const label=document.createElement('strong');label.textContent=titleOf(p);
      const meta=document.createElement('small');meta.textContent=sources.map(x=>x.label).join(' · ');
      card.append(visual,label,meta);fragment.append(card);
    }
    if(fragment.childNodes.length)shelf.replaceChildren(fragment);
    else shelf.textContent=lang==='pl'?'Linki do wydań cyfrowych są uzupełniane.':'Confirmed digital edition links are being added.';
  }
  fetch(root+'data/publications.json',{cache:'no-cache'})
    .then(r=>r.ok?r.json():Promise.reject(Error('Catalogue unavailable')))
    .then(data=>render(Array.isArray(data)?data:[]))
    .catch(()=>{shelf.textContent=lang==='pl'?'Nie udało się załadować wydań.':'Digital editions could not be loaded.';});
})();
