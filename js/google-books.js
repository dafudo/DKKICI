/* The storefront shelf uses only locally cached, title-matched records. */
(() => {
  'use strict';
  const shelf=document.querySelector('[data-google-shelf]');
  if(!shelf)return;
  const lang=document.documentElement.lang==='pl'?'pl':'en';
  const root=document.body.dataset.root || '../';
  const fallback=shelf.dataset.fallback || root+'assets/cover-motivation.svg';
  const safe=(url)=>{try{let u=new URL(url);return u.protocol==='https:'?u.href:null}catch{return null}};
  function render(books) {
    const fragment=document.createDocumentFragment();
    for(const book of books) {
      if(!book.title || !book.cover || !book.slug || !safe(book.url))continue;
      const item=document.createElement('a');
      item.className='gp-book';
      item.href=book.url;
      item.target='_blank';item.rel='noopener noreferrer';
      const visual=document.createElement('div');visual.className='gp-book__visual';
      const image=document.createElement('img');image.loading='lazy';image.decoding='async';
      image.width=360;image.height=480;
      image.src=root+book.cover;
      image.alt=(lang==='pl'?(book.titlePl||book.title):book.title)+' — Google Play Books cover';
      image.addEventListener('error',()=>{image.src=fallback},{once:true});
      const arrow=document.createElement('span');arrow.textContent='↗';arrow.setAttribute('aria-hidden','true');
      visual.append(image,arrow);
      const heading=document.createElement('strong');heading.textContent=(lang==='pl'?(book.titlePl||book.title):book.title);
      const meta=document.createElement('small');meta.textContent='Google Play Books';
      item.append(visual,heading,meta);
      fragment.append(item);
    }
    if(fragment.childNodes.length) shelf.replaceChildren(fragment);
    else shelf.textContent=lang==='pl'?'Wydania są obecnie niedostępne.':'Digital editions are currently unavailable.';
  }
  fetch(root+'data/google-books.json',{cache:'force-cache'})
    .then(r=>r.ok?r.json():Promise.reject(new Error('Catalog unavailable')))
    .then(data=>render(Array.isArray(data)?data:[]))
    .catch(()=>{shelf.textContent=lang==='pl'?'Nie udało się załadować wydań.':'The editions could not be loaded.';});
})();