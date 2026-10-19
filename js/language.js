/* Language selection for bilingual DKK static website.
   Only the English homepage auto-redirects; all deep links keep their URL.
   Manual switches always take precedence over the browser locale. */
(() => {
  'use strict';
  const KEY = 'dkk-preferred-language';
  const path = window.location.pathname;

  const getPreference = () => {
    try {
      const value = window.localStorage.getItem(KEY);
      return value === 'pl' || value === 'en' ? value : null;
    } catch (_) { return null; }
  };
  const setPreference = (locale) => {
    try { window.localStorage.setItem(KEY, locale); } catch (_) {}
  };

  // Register early, so a manual PL / EN switch wins over auto-detection
  // even when the destination is the English homepage.
  document.addEventListener('click', (event) => {
    const target = event.target;
    const link = target?.closest?.('a.locale-link');
    if (!link) return;
    let destination;
    try { destination = new URL(link.href, window.location.href); }
    catch (_) { return; }
    if (destination.origin !== window.location.origin) return;
    const declared = (link.getAttribute('lang') || '').toLowerCase();
    const locale = declared === 'pl' || declared === 'en'
      ? declared
      : /^\/(?:DKKICI\/)?pl(?:\/|$)/i.test(destination.pathname) ? 'pl' : 'en';
    setPreference(locale);
  }, true);

  // We do NOT rewrite addresses that visitors open from LinkedIn, Google,
  // ORCID, or a book record. /pl/ is also always respected when opened directly.
  if (document.documentElement.lang.toLowerCase() !== 'en') return;
  const match = /^\/(?:DKKICI\/)?(?:index\.html)?$/i.exec(path);
  if (!match) return;

  const stored = getPreference();
  const primaryBrowserLanguage =
    (navigator.languages && navigator.languages[0]) ||
    navigator.language || 'en';
  const preferred = stored || (/^pl(?:-|$)/i.test(primaryBrowserLanguage) ? 'pl' : 'en');
  if (preferred !== 'pl') return;

  const base = /^\/DKKICI\//i.test(path) ? '/DKKICI/' : '/';
  const next = new URL(base + 'pl/', window.location.origin);
  next.search = window.location.search;
  next.hash = window.location.hash;
  window.location.replace(next.href);
})();
