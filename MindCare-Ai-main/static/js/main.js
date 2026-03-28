/**
 * MindCare AI – Theme toggle (light/dark). Persist in localStorage.
 * Vanilla JS only.
 */
(function () {
  var KEY = 'mindcare-theme';
  var LIGHT = 'light';
  var DARK = 'dark';

  function getStored() {
    try {
      return localStorage.getItem(KEY) || LIGHT;
    } catch (e) {
      return LIGHT;
    }
  }

  function setStored(val) {
    try {
      localStorage.setItem(KEY, val);
    } catch (e) {}
  }

  function applyTheme(val) {
    var body = document.body;
    if (!body) return;
    if (val === DARK) {
      body.classList.remove('theme-light');
      body.classList.add('theme-dark');
    } else {
      body.classList.remove('theme-dark');
      body.classList.add('theme-light');
    }
  }

  function onToggle() {
    var btn = document.getElementById('themeToggle');
    var current = document.body.classList.contains('theme-dark') ? DARK : LIGHT;
    var next = current === DARK ? LIGHT : DARK;
    applyTheme(next);
    setStored(next);
    if (btn) btn.setAttribute('aria-label', 'Toggle to ' + (next === DARK ? 'light' : 'dark') + ' mode');
  }

  function init() {
    var stored = getStored();
    applyTheme(stored);
    var btn = document.getElementById('themeToggle');
    if (btn) {
      btn.addEventListener('click', onToggle);
      btn.setAttribute('aria-label', 'Toggle to ' + (stored === DARK ? 'light' : 'dark') + ' mode');
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
