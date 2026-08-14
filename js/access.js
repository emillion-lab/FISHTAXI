/* fish.taxi · временен достъп без backend
 *
 * Как работи: кодът се въвежда веднъж, пази се локално, а срещу него
 * се сверява публичен списък с хешове (data/access.json).
 *
 * ЧЕСТНО ЗА ГРАНИЦИТЕ: това е обфускация, не защита. Списъкът е публичен,
 * кодът се проверява на клиента — решен човек може да го заобиколи.
 * Свършва работа срещу случайно споделяне и дава лесно отнемане,
 * което е точно каквото ни трябва сега. Истинската проверка идва
 * с api/ (D1 + Worker), когато има време за него.
 *
 * Всеки код се издава ръчно — и за България, и за чужбина.
 * Разликата е само в основанието:
 *   България → сверена кола в регистъра (mode: 'registry')
 *   Чужбина  → снимки и разговор, на доверие (mode: 'trust')
 */

(function (global) {
  'use strict';

  var PEPPER = 'fishtaxi-access-v1';
  var LIST_URL = '/data/access.json';
  var LS_KEY = 'ft_access';
  var CACHE_KEY = 'ft_access_cache';
  var RECHECK_MS = 3600 * 1000;   // 1 час — отнемането влиза в сила бързо

  function sha256hex(s) {
    var enc = new TextEncoder().encode(s);
    return crypto.subtle.digest('SHA-256', enc).then(function (buf) {
      return Array.prototype.map.call(new Uint8Array(buf), function (b) {
        return b.toString(16).padStart(2, '0');
      }).join('');
    });
  }

  function normalize(code) {
    return String(code || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
  }

  function hashCode(code) {
    return sha256hex(PEPPER + ':' + normalize(code)).then(function (h) {
      return h.slice(0, 16);
    });
  }

  function readLocal() {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || 'null'); }
    catch (e) { return null; }
  }

  function saveLocal(o) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(o)); } catch (e) {}
  }

  function clearLocal() {
    try { localStorage.removeItem(LS_KEY); localStorage.removeItem(CACHE_KEY); } catch (e) {}
  }

  function fetchList() {
    // cache-bust на минута, за да не увисне отнет код в кеша на браузъра
    return fetch(LIST_URL + '?t=' + Math.floor(Date.now() / 60000))
      .then(function (r) { return r.json(); })
      .then(function (j) {
        try { localStorage.setItem(CACHE_KEY, JSON.stringify({ at: Date.now(), list: j })); } catch (e) {}
        return j;
      })
      .catch(function () {
        // без мрежа: работим с последния известен списък
        try {
          var c = JSON.parse(localStorage.getItem(CACHE_KEY) || 'null');
          return c ? c.list : null;
        } catch (e) { return null; }
      });
  }

  function toRecord(hit, h) {
    return {
      hash: h,
      plate: hit.plate || '',
      name: hit.name || '',
      city: hit.city || '',
      country: hit.country || '',
      mode: hit.mode || 'trust',
      role: hit.role || 'driver',
      tier: hit.tier || 'driver',
      level: 'full',
      checked: Date.now()
    };
  }

  /* Въвеждане на код. Един път, после се помни. */
  function redeem(code) {
    return hashCode(code).then(function (h) {
      return fetchList().then(function (list) {
        if (!list) return { ok: false, reason: 'no_network' };
        var hit = (list.drivers || []).filter(function (d) { return d.hash === h; })[0];
        if (!hit) return { ok: false, reason: 'not_found' };
        if (hit.status !== 'active') return { ok: false, reason: hit.status };
        var rec = toRecord(hit, h);
        saveLocal(rec);
        return { ok: true, driver: rec };
      });
    });
  }

  /* Текущо ниво. Сверява списъка на час — така отнемането влиза в сила. */
  function status() {
    var rec = readLocal();
    if (!rec) return Promise.resolve({ level: 'demo', driver: null });

    if (Date.now() - (rec.checked || 0) < RECHECK_MS)
      return Promise.resolve({ level: rec.level, driver: rec });

    return fetchList().then(function (list) {
      if (!list) return { level: rec.level, driver: rec };   // без мрежа не наказваме
      var hit = (list.drivers || []).filter(function (d) { return d.hash === rec.hash; })[0];
      if (!hit || hit.status !== 'active') {
        clearLocal();
        return { level: 'demo', driver: null, revoked: true };
      }
      var fresh = toRecord(hit, rec.hash);
      saveLocal(fresh);
      return { level: 'full', driver: fresh };
    });
  }

  function isAdmin() {
    var r = readLocal();
    return !!(r && r.role === 'admin');
  }

  function signOut() { clearLocal(); }

  global.FTAccess = {
    redeem: redeem,
    status: status,
    signOut: signOut,
    isAdmin: isAdmin,
    current: readLocal
  };
})(window);
