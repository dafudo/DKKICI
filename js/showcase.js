/* Small, accessible enhancements for archival pages. No frontend framework. */
(() => {
 'use strict';
 const lang=document.documentElement.lang==='pl'?'pl':'en';
 const gallery=document.querySelector('[data-gallery-list]');
 const modal=document.querySelector('#photo-viewer');
 let opener=null;
 if(gallery){
   const buttons=[...document.querySelectorAll('[data-gallery-filter]')];
   const items=[...gallery.querySelectorAll('[data-gallery-item]')];
   const count=document.querySelector('[data-gallery-count]');
   buttons.forEach(button=>button.addEventListener('click',()=>{
     const type=button.dataset.galleryFilter;
     buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
     let n=0;
     for(const item of items){
       const show=type==='all'||item.dataset.galleryItem===type;
       item.hidden=!show;if(show)n++;
     }
     if(count)count.textContent=String(n).padStart(2,'0');
   }));
   if(modal){
     const img=modal.querySelector('[data-photo-full]');
     const title=modal.querySelector('[data-photo-title]');
     const counter=modal.querySelector('[data-photo-label]');
     gallery.addEventListener('click',event=>{
       const link=event.target.closest('a[data-gallery-open]');
       if(!link||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
       event.preventDefault();
       opener=link;
       img.src=link.dataset.galleryOpen;
       img.alt=link.dataset.alt||'';
       title.textContent=link.dataset.title||'';
       counter.textContent=link.dataset.section||'';
       if(!modal.open)modal.showModal();
       document.body.classList.add('modal-open');
     });
     modal.querySelector('[data-gallery-close]')?.addEventListener('click',()=>modal.close());
     modal.addEventListener('click',event=>{if(event.target===modal)modal.close()});
     modal.addEventListener('close',()=>{
       document.body.classList.remove('modal-open');
       img.removeAttribute('src');
       opener?.focus({preventScroll:true});
     });
   }
 }

 // Each publication has a canonical shareable URL, distinct from any retailer link.
 // The button must copy that URL rather than the current browser URL containing query strings.
 for (const button of document.querySelectorAll('[data-copy-link]')) {
   button.addEventListener('click', async () => {
     const canonical=document.querySelector('link[rel="canonical"]')?.href || location.href.split(/[?#]/)[0];
     const original=button.dataset.labelOriginal || button.textContent;
     button.dataset.labelOriginal=original;
     try {
       if (!navigator.clipboard?.writeText) throw new Error('Clipboard not available');
       await navigator.clipboard.writeText(canonical);
       button.textContent=button.dataset.copied || (lang==='pl'?'Skopiowano':'Copied');
     } catch (_) {
       button.textContent=button.dataset.failed || (lang==='pl'?'Skopiuj adres z przeglądarki':'Copy from address bar');
     }
     button.setAttribute('aria-live','polite');
     window.setTimeout(()=>{button.textContent=original;},2000);
   });
 }
 const filters=[...document.querySelectorAll('[data-archive-filter]')];
 const entries=[...document.querySelectorAll('[data-archive-card]')];
 if(filters.length && entries.length){
   filters.forEach(b=>b.addEventListener('click',()=>{
     const topic=b.dataset.archiveFilter;
     filters.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
     let n=0;
     entries.forEach(card=>{
       const show=topic==='all'||card.dataset.archiveCard===topic;
       card.hidden=!show;
       if(show)n++;
     });
     const label=document.querySelector('[data-media-counter]');
     if(label)label.textContent=String(n).padStart(2,'0');
   }));
 }
})();