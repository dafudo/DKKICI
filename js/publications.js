/* DKK Publications: progressive enhancement, no framework. */
(() => {
  'use strict';
  const root = document.body.dataset.root || '../';
  const lang = document.documentElement.lang === 'pl' ? 'pl' : 'en';
  const tr = lang === 'pl' ? {
    open:'Otwórz szczegóły',empty:'Nie znaleziono publikacji. Spróbuj innego hasła.', year:'Rok',
    format:'Rodzaj',topic:'Tematyka',preview:'Dane wydawnicze w przygotowaniu',links:'Gdzie przeczytać',
    coming:'Linki do księgarni zostaną dodane po potwierdzeniu dostępności.',
    full:'Pełna strona publikacji',copy:'Kopiuj link',copied:'Skopiowano',
    results:'publikacji',other:'Dostępne wydania'
  } : {
    open:'Explore publication',empty:'No publications match. Try another search.',year:'Year',
    format:'Format',topic:'Topic',preview:'Publication details to be confirmed',links:'Where to read',
    coming:'Store links will appear here after availability is confirmed.',
    full:'Full publication page',copy:'Copy link',copied:'Copied',
    results:'publications',other:'Available editions'
  };
  const grid = document.querySelector('[data-publications-grid]');
  const search = document.querySelector('[data-publication-search]');
  const chips = [...document.querySelectorAll('[data-category]')];
  const count = document.querySelector('[data-publication-count]');
  const countWord = document.querySelector('[data-publication-word]');
  const empty = document.querySelector('[data-publication-empty]');
  const order = document.querySelector('[data-publication-sort]');
  const dialog = document.querySelector('#publication-dialog');
  const cover = dialog?.querySelector('[data-dialog-cover]');
  const title = dialog?.querySelector('[data-dialog-title]');
  const subtitle = dialog?.querySelector('[data-dialog-subtitle]');
  const description = dialog?.querySelector('[data-dialog-description]');
  const facts = dialog?.querySelector('[data-dialog-facts]');
  const links = dialog?.querySelector('[data-dialog-links]');
  const linkMessage = dialog?.querySelector('[data-dialog-link-message]');
  const full = dialog?.querySelector('[data-dialog-full]');
  const copy = dialog?.querySelector('[data-dialog-copy]');
  let items = [], category = 'all', current = null, opener = null;
  const detailPath = p => root + (lang === 'pl' ? 'pl/publikacje/' : 'works/') + encodeURIComponent(p.slug) + '/';
  const titleOf = p => p.title?.[lang] || p.title?.en || '';
  const details = p => p.description?.[lang] || p.description?.en || '';
  const subtitleOf = p => p.subtitle?.[lang] || p.subtitle?.en || '';
  const asText = (element, value) => { if(element) element.textContent = String(value ?? ''); };
  const validUrl = value => {
    try { const u = new URL(value); return u.protocol === 'https:' ? u.href : ''; } catch { return ''; }
  };
  const labelFor = (kind, value) => ({
    book:{en:'Book',pl:'Książka'},journal:{en:'Journal',pl:'Czasopismo'},
    article:{en:'Research article',pl:'Artykuł naukowy'},research:{en:'Research paper',pl:'Opracowanie badawcze'},working_paper:{en:'Working paper',pl:'Opracowanie robocze'},resource:{en:'Resource',pl:'Materiał'},
    psychology:{en:'Psychology',pl:'Psychologia'},education:{en:'Education',pl:'Edukacja'},
    practice:{en:'Practice',pl:'Praktyka'},ideas:{en:'Ideas',pl:'Idee'}
  }[value]?.[lang] || value || '');

  function createCard(p,i) {
    const card = document.createElement('a');
    card.className = 'publication-tile' + (p.spotlight ? ' publication-tile--spotlight' : '');
    card.href = detailPath(p);
    card.setAttribute('aria-label', tr.open + ': ' + titleOf(p));
    card.style.setProperty('--tile-index', String(Math.min(i,11)));
    const frame=document.createElement('div');
    frame.className='publication-tile__frame';
    const img=document.createElement('img');
    img.loading='lazy'; img.decoding='async'; img.src=root + p.cover;
    img.alt=titleOf(p) + (lang === 'pl' ? ' — okładka publikacji' : ' — cover'); img.width=660;img.height=880;
    const symbol=document.createElement('span');symbol.className='publication-tile__arrow';symbol.textContent='↗';symbol.setAttribute('aria-hidden','true');
    frame.append(img,symbol);
    const meta=document.createElement('div');meta.className='publication-tile__meta';
    meta.textContent=labelFor(null,p.kind) + ' / ' + (p.year || '');
    const name=document.createElement('h3'); name.textContent=p.titleShort?.[lang]||titleOf(p);
    const sub=document.createElement('p');sub.textContent=subtitleOf(p);
    card.append(frame,meta,name,sub);
    card.addEventListener('click', e=>{
      if(e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault(); opener=card; showPublication(p,true);
    });
    return card;
  }

  function render() {
    const q=(search?.value || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().trim();
    const matched=items.filter(p=>{
      if(p.status!=='published')return false;
      if(category!=='all' && p.category!==category)return false;
      const hay=[p.title?.en,p.title?.pl,p.subtitle?.en,p.subtitle?.pl,p.description?.en,p.description?.pl,p.kind,p.year].join(' ').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
      return !q || hay.includes(q);
    }).sort((a,b)=>{
      const dir=order?.value;
      return dir==='oldest' ? a.date.localeCompare(b.date) : dir==='title' ? titleOf(a).localeCompare(titleOf(b),lang) : b.date.localeCompare(a.date);
    });
    grid.replaceChildren(...matched.map(createCard));
    asText(count, String(matched.length));
    asText(countWord, window.DKKPublicationWord(matched.length,lang));
    if(empty)empty.hidden=matched.length!==0;
  }
  function makeExternal(url,label) {
    const a=document.createElement('a');a.className='pub-store-link';a.href=url;a.target='_blank';a.rel='noopener noreferrer';
    a.textContent=label;const arrow=document.createElement('span');arrow.textContent='↗';arrow.setAttribute('aria-hidden','true');a.append(arrow);
    return a;
  }
  function showPublication(p, push=true) {
    if(!dialog || !p)return;
    current=p;dialog.classList.toggle('is-long-title',titleOf(p).length>62);asText(title,titleOf(p));asText(subtitle,subtitleOf(p));asText(description,details(p));
    cover.src=root+p.cover;cover.alt=titleOf(p) + (lang === 'pl' ? ' — okładka publikacji' : ' — cover');
    facts.replaceChildren();
    [[tr.year,p.year],[tr.format,labelFor(null,p.kind)],[tr.topic,labelFor(null,p.category)]].forEach(([k,v])=>{
      const line=document.createElement('div');const label=document.createElement('span');label.textContent=k;
      const val=document.createElement('strong');val.textContent=v;line.append(label,val);facts.append(line);
    });
    links.replaceChildren();
    const available=[...(p.links||[])].filter(x=>validUrl(x.url));
    available.forEach(x=>links.append(makeExternal(validUrl(x.url),x.label || (lang === 'pl' ? 'Źródło publikacji' : 'Publication source'))));
    linkMessage.hidden=available.length>0;
    asText(linkMessage,tr.coming);
    full.href=detailPath(p);
    if(!dialog.open)dialog.showModal();
    document.body.classList.add('modal-open');
    if(push) {
      const u=new URL(location.href);u.searchParams.set('publication',p.slug);
      history.pushState({publication:p.slug},'',u);
    }
  }
  function removeParam() {
    const u=new URL(location.href);
    if(u.searchParams.has('publication')){u.searchParams.delete('publication');history.replaceState(null,'',u);}
  }
  dialog?.querySelector('[data-dialog-close]')?.addEventListener('click',()=>dialog.close());
  dialog?.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
  dialog?.addEventListener('close',()=>{
    document.body.classList.remove('modal-open');current=null;removeParam();opener?.focus({preventScroll:true});
  });
  copy?.addEventListener('click',async()=>{
    if(!current)return;
    const target=new URL(detailPath(current),location.href).href;
    try{await navigator.clipboard.writeText(target);asText(copy,tr.copied);}
    catch{asText(copy,tr.copy);}
    window.setTimeout(()=>asText(copy,tr.copy),1700);
  });
  chips.forEach(chip=>chip.addEventListener('click',()=>{
    category=chip.dataset.category;
    chips.forEach(b=>b.setAttribute('aria-pressed',String(b===chip)));
    render();
  }));
  search?.addEventListener('input',render);
  order?.addEventListener('change',render);
  window.addEventListener('popstate',()=>{
    const slug=new URL(location.href).searchParams.get('publication');
    const target=items.find(p=>p.slug===slug && p.status==='published');
    if(target)showPublication(target,false);else if(dialog?.open)dialog.close();
  });

  // Featured collection is pre-rendered from publications.json by the generator.
  // The catalogue remains readable without JavaScript; JS adds navigation and the modal.
  function initFeaturedSlider() {
    const slider = document.querySelector('[data-featured-slider]');
    if (!slider) return;
    const slides = [...slider.querySelectorAll('[data-featured-slide]')];
    if (!slides.length) return;
    const prev = document.querySelector('[data-featured-prev]');
    const next = document.querySelector('[data-featured-next]');
    const current = document.querySelector('[data-featured-current]');
    const dots = [...document.querySelectorAll('[data-featured-dot]')];
    let active = 0, startX = null, startY = null;

    function goTo(index) {
      active = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => {
        const selected = i === active;
        slide.hidden = !selected;
        slide.classList.toggle('is-active', selected);
      });
      dots.forEach((dot, i) => dot.setAttribute('aria-current', String(i === active)));
      if (current) current.textContent = String(active + 1).padStart(2, '0');
    }
    prev?.addEventListener('click', () => goTo(active - 1));
    next?.addEventListener('click', () => goTo(active + 1));
    dots.forEach((dot, i) => dot.addEventListener('click', () => goTo(i)));
    slider.addEventListener('keydown', event => {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault();
        goTo(active + (event.key === 'ArrowRight' ? 1 : -1));
      }
    });
    slider.addEventListener('touchstart', event => {
      if (event.touches.length !== 1) return;
      startX = event.touches[0].clientX;
      startY = event.touches[0].clientY;
    }, {passive:true});
    slider.addEventListener('touchend', event => {
      if (startX === null || !event.changedTouches.length) return;
      const dx = event.changedTouches[0].clientX - startX;
      const dy = event.changedTouches[0].clientY - startY;
      startX = startY = null;
      if (slides.length > 1 && Math.abs(dx) >= 50 && Math.abs(dx) > Math.abs(dy) * 1.3) {
        goTo(active + (dx < 0 ? 1 : -1));
      }
    }, {passive:true});
    slider.addEventListener('touchcancel', () => { startX = startY = null; });
    goTo(0);

    const more = document.querySelector('[data-featured-expand]');
    const modal = document.querySelector('[data-featured-dialog]');
    if (more && modal && typeof modal.showModal === 'function') {
      more.addEventListener('click', () => {
        modal.showModal();
        document.body.classList.add('modal-open');
      });
      modal.querySelector('[data-featured-close]')?.addEventListener('click', () => modal.close());
      modal.addEventListener('click', event => {
        if (event.target === modal) modal.close();
      });
      modal.addEventListener('close', () => {
        document.body.classList.remove('modal-open');
        more.focus({preventScroll:true});
      });
    }
  }
  initFeaturedSlider();

  fetch(root+'data/publications.json',{cache:'no-cache'})
    .then(r=>{if(!r.ok)throw new Error('Publication data unavailable');return r.json();})
    .then(data=>{
      if(!Array.isArray(data))throw new Error('Invalid publication catalogue');
      items=data.filter(p=>p?.slug && p.title && p.cover && p.status==='published');
      render();
      const slug=new URL(location.href).searchParams.get('publication');
      const selected=items.find(p=>p.slug===slug);
      if(selected)showPublication(selected,false);
    })
    .catch(()=>{
      if(empty){empty.hidden=false;empty.textContent=lang==='pl'?'Nie udało się wczytać katalogu. Odśwież stronę.':'The catalogue could not be loaded. Please refresh.';}
    });
})();