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
 * Двата пътя:
 *   България  → код се издава ръчно след проверка на кола + Viber/WhatsApp
 *   Чужбина   → самообслужване, локален код, ниво 'trust' (на доверие)
 */

(function (global) {
  'use strict';

  var PEPPER = 'fishtaxi-access-v1';
  var LIST_URL = '/data/access.json';
  var LS_KEY = 'ft_access';
  var CACHE_KEY = 'ft_access_cache';
  var RECHECK_MS = 6 * 3600 * 1000;   // сверявай списъка веднъж на 6 часа

  var AL = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';   // без 0/O/1/I — за диктовка по телефона

  function sha256hex(s) {
    var enc = new TextEncoder().encode(s);
    return crypto.subtle.digest('SHA-256', enc).then(function (buf) {
      return Array.prototype.map.call(new Uint8Array(buf), function (b) {
        return b.toString(16).padStart(2, '0');
      }).join('');
    });
  }

  function hashCode(code) {
    return sha256hex(PEPPER + ':' + normalize(code)).then(function (h) {
      return h.slice(0, 16);
    });
  }

  function normalize(code) {
    return String(code || '').toUpperCase().replace(/[^A-Z0-9]/g, '')
      .replace(/O/g, '0').replace(/I/g, '1')   // чести грешки при преписване
      .replace(/0/g, 'O').replace(/1/g, 'J');  // връщаме към азбуката ни
  }

  function selfCode() {
    var out = '', a = new Uint8Array(8);
    crypto.getRandomValues(a);
    for (var i = 0; i < 8; i++) out += AL[a[i] % AL.length];
    return out;
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
    // cache-bust, за да не увисне отнет код в кеша на браузъра
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

  /* Въвеждане на код, издаден от Емил (България). */
  function redeem(code) {
    return hashCode(code).then(function (h) {
      return fetchList().then(function (list) {
        if (!list) return { ok: false, reason: 'no_network' };
        var hit = (list.drivers || []).filter(function (d) { return d.hash === h; })[0];
        if (!hit) return { ok: false, reason: 'not_found' };
        if (hit.status !== 'active') return { ok: false, reason: hit.status };

        var rec = {
          hash: h, plate: hit.plate, name: hit.name, city: hit.city,
          country: hit.country, mode: hit.mode || 'registry',
          tier: hit.tier || 'driver', level: 'full',
          checked: Date.now()
        };
        saveLocal(rec);
        return { ok: true, driver: rec };
      });
    });
  }

  /* Самообслужване извън България — без проверка, на доверие. */
  function selfRegister(info) {
    var rec = {
      hash: null, code: selfCode(),
      plate: (info && info.plate) || '',
      name: (info && info.name) || '',
      city: (info && info.city) || '',
      country: (info && info.country) || '',
      mode: 'trust', tier: 'driver', level: 'full',
      checked: Date.now()
    };
    saveLocal(rec);
    return rec;
  }

  /* Текущо ниво. Периодично сверява списъка — така отнемането влиза в сила. */
  function status() {
    var rec = readLocal();
    if (!rec) return Promise.resolve({ level: 'demo', driver: null });

    // Чуждите записи не са в списъка — няма какво да се сверява.
    if (rec.mode === 'trust') return Promise.resolve({ level: 'full', driver: rec });

    if (Date.now() - (rec.checked || 0) < RECHECK_MS)
      return Promise.resolve({ level: rec.level, driver: rec });

    return fetchList().then(function (list) {
      if (!list) return { level: rec.level, driver: rec };   // без мрежа не наказваме
      var hit = (list.drivers || []).filter(function (d) { return d.hash === rec.hash; })[0];
      if (!hit || hit.status !== 'active') {
        clearLocal();
        return { level: 'demo', driver: null, revoked: true };
      }
      rec.checked = Date.now();
      rec.tier = hit.tier || rec.tier;
      saveLocal(rec);
      return { level: 'full', driver: rec };
    });
  }

  function signOut() { clearLocal(); }

  global.FTAccess = {
    redeem: redeem,
    selfRegister: selfRegister,
    status: status,
    signOut: signOut,
    current: readLocal
  };
})(window);
