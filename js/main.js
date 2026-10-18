/* Progressive enhancement only: no framework, no mandatory runtime. */
(() => {
  'use strict';
  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];
  $$('img[data-fallback]').forEach(img => img.addEventListener('error',()=> { if(img.src !== new URL(img.dataset.fallback,window.location.href).href) img.src=img.dataset.fallback; }));
  const nav = $('.site-nav');
  const updateNav = () => nav?.classList.toggle('is-scrolled', window.scrollY > 45);
  updateNav();
  window.addEventListener('scroll', updateNav, { passive: true });

  const menuButton = $('[data-menu-toggle]');
  const menu = $('.mobile-panel');
  const closeMenu = () => {
    menu?.classList.remove('is-open');
    document.body.classList.remove('menu-open');
    menuButton?.setAttribute('aria-expanded','false');
    menu?.setAttribute('aria-hidden','true');
  };
  menuButton?.addEventListener('click', () => {
    const open = !menu.classList.contains('is-open');
    menu.classList.toggle('is-open',open);
    document.body.classList.toggle('menu-open',open);
    menuButton.setAttribute('aria-expanded',String(open));
    menu.setAttribute('aria-hidden',String(!open));
    if(open) $('nav a',menu)?.focus();
  });
  $$('a',menu || document.createElement('div')).forEach(a => a.addEventListener('click',closeMenu));
  window.addEventListener('keydown', e => { if(e.key==='Escape') closeMenu(); });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if(entry.isIntersecting){ entry.target.classList.add('is-visible'); observer.unobserve(entry.target); }
      });
    }, { threshold: .08, rootMargin: '0px 0px -28px 0px' });
    $$('.reveal').forEach(el => observer.observe(el));
  } else $$('.reveal').forEach(el=>el.classList.add('is-visible'));

  const filterButtons = $$('[data-filter]');
  const search = $('[data-search]');
  const cards = $$('[data-work-card]');
  const counter = $('[data-archive-count]');
  const empty = $('[data-empty]');
  let currentFilter = 'all';
  const update = () => {
    const q = (search?.value || '').toLocaleLowerCase().trim();
    let visible = 0;
    cards.forEach(card => {
      const matchType = currentFilter === 'all' || card.dataset.category === currentFilter;
      const matchText = !q || (card.dataset.search || '').toLocaleLowerCase().includes(q);
      const show = matchType && matchText;
      card.hidden = !show;
      if(show)visible++;
    });
    if(counter)counter.textContent = String(visible).padStart(2,'0');
    if(empty)empty.style.display = visible === 0 ? 'block' : 'none';
  };
  filterButtons.forEach(button => button.addEventListener('click',() => {
    currentFilter = button.dataset.filter;
    filterButtons.forEach(b => b.setAttribute('aria-pressed',String(b === button)));
    update();
  }));
  search?.addEventListener('input',update);
  update();

  const modal = $('[data-film-modal]');
  const openFilm = $('[data-open-film]');
  const modalClose = $('[data-close-film]');
  const filmVideo = modal && $('video',modal);
  const closeFilm = () => {
    if(!modal)return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden','true');
    document.body.classList.remove('modal-open');
    filmVideo?.pause();
    openFilm?.focus();
  };
  openFilm?.addEventListener('click',() => {
    modal?.classList.add('is-open');
    modal?.setAttribute('aria-hidden','false');
    document.body.classList.add('modal-open');
    modalClose?.focus();
    if(filmVideo && filmVideo.querySelector('source'))filmVideo.play().catch(()=>{});
  });
  modalClose?.addEventListener('click',closeFilm);
  modal?.addEventListener('click',e => { if(e.target === modal)closeFilm(); });
  window.addEventListener('keydown',e=> { if(e.key==='Escape' && modal?.classList.contains('is-open'))closeFilm(); });

  $$('[data-copy-link]').forEach(btn => btn.addEventListener('click',async()=>{
    const old = btn.textContent;
    try {
      await navigator.clipboard.writeText(window.location.href);
      btn.textContent = btn.dataset.copied || 'Copied';
    } catch {
      const helper = document.createElement('textarea');
      helper.value = window.location.href; document.body.appendChild(helper);helper.select();
      const success = document.execCommand('copy'); helper.remove();
      btn.textContent = success ? (btn.dataset.copied || 'Copied') : (btn.dataset.failed || 'Copy unavailable');
    }
    window.setTimeout(()=>btn.textContent=old,2300);
  }));
})();
