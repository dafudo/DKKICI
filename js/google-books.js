/* Optional enrichment for user-provided Google Play Books volume IDs. */
(() => {
 const shelf=document.querySelector('[data-google-shelf]');
 if(!shelf)return;
 const codes=['rIMbEgAAQBAJ','mZMaEgAAQBAJ','0voaEgAAQBAJ','Jh8cEgAAQBAJ','C3ocEgAAQBAJ'];
 const pl=document.documentElement.lang==='pl';
 const fallback=shelf.dataset.fallback || '../assets/cover-motivation.svg';
 const root=document.createDocumentFragment();
 codes.forEach((id,i)=>{
   const card=document.createElement('a');card.className='gp-book';
   card.href='https://play.google.com/store/books/details?id='+encodeURIComponent(id);
   card.target='_blank';card.rel='noopener noreferrer';
   const visual=document.createElement('div');visual.className='gp-book__visual';
   const img=document.createElement('img');img.loading='lazy';img.decoding='async';
   img.width=360;img.height=480;img.alt=pl?'Okładka książki Google Play Books':'Google Play Books cover';
   img.src='https://books.google.com/books/content?id='+encodeURIComponent(id)+'&printsec=frontcover&img=1&zoom=1&source=gbs_api';
   img.onerror=()=>{img.onerror=null;img.src=fallback;};
   const badge=document.createElement('span');badge.textContent='↗';visual.append(img,badge);
   const title=document.createElement('strong');title.textContent=(pl?'Wydanie Google Play':'Google Play edition')+' '+String(i+1).padStart(2,'0');
   const sub=document.createElement('small');sub.textContent='Google Play Books';
   card.append(visual,title,sub);root.append(card);
   fetch('https://www.googleapis.com/books/v1/volumes/'+encodeURIComponent(id),{mode:'cors',cache:'force-cache'})
     .then(r=>r.ok?r.json():Promise.reject(new Error('Google Books API unavailable')))
     .then(data=>{
       const info=data.volumeInfo||{};
       const authors=(info.authors||[]).join(' ').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
       if(authors.includes('kolodziej')&&typeof info.title==='string')title.textContent=info.title;
       const source=info.imageLinks?.thumbnail||info.imageLinks?.smallThumbnail;
       if(source&&/^https?:\/\//.test(source))img.src=source.replace(/^http:/,'https:');
     }).catch(()=>{});
 });
 shelf.replaceChildren(root);
})();