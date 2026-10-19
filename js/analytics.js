/* Optional, consent-based Google Analytics 4 for DKKICI.
   No Google request, cookie or event is sent before analytics consent. */
(() => {
  'use strict';

  const node = document.querySelector('script[data-dkk-analytics]');
  const id = node?.dataset.measurementId || '';
  if (!/^G-[A-Z0-9]+$/.test(id)) return;

  const KEY = 'dkk-analytics-consent-v1';
  const isPL = document.documentElement.lang.toLowerCase().startsWith('pl');
  const copy = isPL ? {
    title: 'Prywatność i statystyki',
    message: 'Opcjonalne statystyki Google Analytics pomagają mi zrozumieć, jak korzystasz ze strony. Pomiar rozpocznie się wyłącznie po wyrażeniu zgody. Możesz zmienić wybór w stopce.',
    accept: 'Zgadzam się',
    decline: 'Tylko niezbędne',
    settings: 'Ustawienia prywatności',
    policy: 'Polityka Google dotycząca prywatności'
  } : {
    title: 'Privacy and analytics',
    message: 'Optional Google Analytics helps me understand how this website is used. Tracking starts only if you agree. You can change your choice in the footer.',
    accept: 'Allow analytics',
    decline: 'Necessary only',
    settings: 'Privacy settings',
    policy: 'Google privacy policy'
  };

  const readChoice = () => {
    try {
      const value = localStorage.getItem(KEY);
      return value === 'granted' || value === 'denied' ? value : null;
    } catch (_) { return null; }
  };
  const saveChoice = value => {
    try { localStorage.setItem(KEY, value); } catch (_) {}
  };

  let started = false;
  function startAnalytics() {
    if (started) return;
    started = true;

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'granted',
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied'
    });
    window.gtag('js', new Date());
    window.gtag('config', id, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });

    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(tag);
  }

  const banner = document.createElement('section');
  banner.className = 'dkk-consent';
  banner.setAttribute('role', 'region');
  banner.setAttribute('aria-labelledby', 'dkk-consent-title');
  banner.hidden = true;

  const title = document.createElement('h2');
  title.id = 'dkk-consent-title';
  title.textContent = copy.title;
  const desc = document.createElement('p');
  desc.textContent = copy.message;
  const link = document.createElement('a');
  link.href = 'https://policies.google.com/privacy';
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  link.textContent = copy.policy;
  const actions = document.createElement('div');
  actions.className = 'dkk-consent__actions';
  const accept = document.createElement('button');
  accept.type = 'button';
  accept.textContent = copy.accept;
  accept.className = 'dkk-consent__accept';
  const decline = document.createElement('button');
  decline.type = 'button';
  decline.textContent = copy.decline;
  decline.className = 'dkk-consent__decline';
  actions.append(accept, decline);
  banner.append(title, desc, link, actions);
  document.body.appendChild(banner);

  function choose(value) {
    saveChoice(value);
    banner.hidden = true;
    if (value === 'granted') {
      startAnalytics();
    } else if (started && typeof window.gtag === 'function') {
      window.gtag('consent', 'update', {
        analytics_storage: 'denied',
        ad_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied'
      });
    }
  }
  accept.addEventListener('click', () => choose('granted'));
  decline.addEventListener('click', () => choose('denied'));

  const footer = document.querySelector('.footer-bottom') || document.querySelector('footer');
  if (footer) {
    const settings = document.createElement('button');
    settings.type = 'button';
    settings.className = 'dkk-consent-settings';
    settings.textContent = copy.settings;
    settings.addEventListener('click', () => {
      banner.hidden = false;
      accept.focus();
    });
    footer.appendChild(settings);
  }

  if (readChoice() === 'granted') startAnalytics();
  else if (!readChoice()) banner.hidden = false;
})();
