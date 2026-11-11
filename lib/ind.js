/* fish.taxi — индустриален слой, поведение (11.11.2026).
   Зарежда се СЛЕД главния скрипт и обвива функциите му по име:
   renderMap (жива карта), openMod/closeMod (лист отдолу), showTab (преходи),
   render (появяване на картите, табела с номер), поръчка/обаждане (вибрация).
   При „намалено движение“ няма анимации, само мигновени промени. */
(function () {
  'use strict';
  if (window.__IND) return;
  window.__IND = 1;

  var RM = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var NEAR_KM = 60;
  var L10N = {
    bg: { on: 'онлайн', of: 'шофьора', upd: 'обновено', ago: 'преди', s: 'с', m: 'мин', now: 'сега' },
    en: { on: 'online', of: 'drivers', upd: 'updated', ago: '', s: 's ago', m: 'min ago', now: 'now' }
  };
  function tx() { return L10N[window.lang] || L10N.en; }
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function byId(id) { return (window.DRIVERS || []).filter(function (d) { return d.id === id; })[0]; }
  function km(a, b, c, d) { return typeof haversineKm === 'function' ? haversineKm(a, b, c, d) : 9999; }
  function buzz(p) { try { if (navigator.vibrate) navigator.vibrate(p); } catch (e) {} }
  function wrap(name, after, before) {
    var orig = window[name];
    if (typeof orig !== 'function') return;
    window[name] = function () {
      if (before && before.apply(this, arguments) === false) return;
      var r = orig.apply(this, arguments);
      if (after) after.apply(this, arguments);
      return r;
    };
    window[name].__orig = orig;
  }

  /* ── табела с рег. номер ── */
  var BG_PLATE = /^[A-ZА-Я]{1,2}\s?\d{4}\s?[A-ZА-Я]{1,2}$/i;
  function plate(p) {
    if (!p) return '';
    return '<span class="ind-plate"><i>' + (BG_PLATE.test(p.trim()) ? 'BG' : '&nbsp;') + '</i><b>' + esc(p) + '</b></span>';
  }

  /* ── 1. Жива карта ── */
  var skipFly = false, MK = {}, selId = null, lastPoll = 0, hud = null, firstMap = true;
  function iconFor(d, sel) {
    var src = d.avatar || (d.photos && d.photos[0]) || '';
    var inner = src ? '<img src="' + esc(src) + '" alt="">' : '<span>' + (typeof carI === 'function' ? carI(d) : '🚕') + '</span>';
    var name = String((window.lang === 'bg' && d.name_bg) || d.name || '').split(' ')[0];
    return L.divIcon({
      className: 'ind-mki', iconSize: [44, 44], iconAnchor: [22, 22],
      html: '<div class="ind-mk ' + (d.online ? 'on' : 'off') + (sel ? ' sel' : '') + '"><span class="ring"></span>' +
        '<div class="av">' + inner + '</div><span class="dot"></span><b class="tag">' + esc(name) + '</b></div>'
    });
  }
  function tween(m, to) {
    var from = m.getLatLng();
    var dist = km(from.lat, from.lng, to[0], to[1]);
    if (m._indRaf) cancelAnimationFrame(m._indRaf);
    if (RM || dist < 0.003 || dist > 5) { m.setLatLng(to); return; }
    var t0 = performance.now(), D = 1600;
    function step(t) {
      var k = Math.min(1, (t - t0) / D);
      k = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      m.setLatLng([from.lat + (to[0] - from.lat) * k, from.lng + (to[1] - from.lng) * k]);
      if (k < 1) m._indRaf = requestAnimationFrame(step);
    }
    m._indRaf = requestAnimationFrame(step);
  }
  function flyTo(d) {
    if (!window.map || !d || !d.lat) return false;
    var c = map.getCenter();
    if (km(c.lat, c.lng, d.lat, d.lng) > NEAR_KM) return false;
    var z = Math.max(map.getZoom(), 15);
    if (RM) map.setView([d.lat, d.lng], z); else map.flyTo([d.lat, d.lng], z, { duration: .85 });
    return true;
  }
  function select(id) {
    selId = id;
    Object.keys(MK).forEach(function (k) {
      var el = MK[k].m.getElement && MK[k].m.getElement();
      var mk = el && el.querySelector('.ind-mk');
      if (mk) mk.classList.toggle('sel', +k === id);
      if (+k === id) MK[k].m.setZIndexOffset(1000); else MK[k].m.setZIndexOffset(MK[k].on ? 500 : 0);
    });
  }
  function renderMap() {
    if (!window.mapReady || !window.map) return;
    if (window.mkrs && mkrs.length) { mkrs.forEach(function (m) { try { m.remove(); } catch (e) {} }); mkrs = []; }
    var seen = {};
    (window.DRIVERS || []).forEach(function (d) {
      if (d.lat == null || d.lng == null) return;
      seen[d.id] = 1;
      var e = MK[d.id];
      if (!e) {
        var m = L.marker([d.lat, d.lng], { icon: iconFor(d, d.id === selId), zIndexOffset: d.online ? 500 : 0 }).addTo(map);
        m.on('click', function () {
          buzz(8);
          select(d.id);
          var flew = flyTo(d);
          skipFly = true;
          setTimeout(function () { openMod(d.id); }, flew && !RM ? 480 : 0);
        });
        MK[d.id] = { m: m, on: !!d.online, src: d.avatar };
      } else {
        if (e.on !== !!d.online) {
          e.on = !!d.online;
          e.m.setIcon(iconFor(d, d.id === selId));
          e.m.setZIndexOffset(d.id === selId ? 1000 : (d.online ? 500 : 0));
        }
        tween(e.m, [d.lat, d.lng]);
      }
    });
    Object.keys(MK).forEach(function (k) { if (!seen[k]) { MK[k].m.remove(); delete MK[k]; } });
    if (!firstMap) {
      var top = document.querySelector('.top');
      if (top && !RM) { top.classList.remove('ind-tick'); void top.offsetWidth; top.classList.add('ind-tick'); }
      if (hud && !RM) { hud.classList.remove('blink'); void hud.offsetWidth; hud.classList.add('blink'); }
    }
    firstMap = false;
    lastPoll = Date.now();
    drawHud(true);
  }
  window.renderMap = renderMap;

  /* табло: онлайн / общо / преди колко секунди */
  var hudOn = -1;
  function drawHud(changed) {
    if (!hud) return;
    var ds = window.DRIVERS || [], on = ds.filter(function (d) { return d.online; }).length, t = tx();
    var s = Math.round((Date.now() - lastPoll) / 1000), pre = t.ago ? t.ago + ' ' : '';
    var age = !lastPoll ? '—' : s < 3 ? t.now : s < 90 ? pre + s + ' ' + t.s : pre + Math.round(s / 60) + ' ' + t.m;
    if (!hud.__n) {
      hud.innerHTML = '<span class="lv"></span><b></b> <span></span> <i></i><br><i></i>';
      hud.__n = hud.querySelector('b'); hud.__l = hud.querySelector('span:not(.lv)');
      var ii = hud.querySelectorAll('i'); hud.__tot = ii[0]; hud.__age = ii[1];
    }
    hud.__l.textContent = t.on;
    hud.__tot.textContent = '/ ' + ds.length + ' ' + t.of;
    hud.__age.textContent = t.upd + ' ' + age;
    if (changed && hudOn >= 0 && hudOn !== on && !RM) countTo(hud.__n, hudOn, on);
    else if (!hud.__counting) hud.__n.textContent = on;
    hudOn = on;
  }
  function countTo(el, a, b) {
    hud.__counting = 1;
    var t0 = performance.now();
    (function step(t) {
      var k = Math.min(1, (t - t0) / 600);
      el.textContent = Math.round(a + (b - a) * k);
      if (k < 1) requestAnimationFrame(step); else hud.__counting = 0;
    })(t0);
  }
  function addHud() {
    if (hud || !window.map || !L.Control) return;
    var C = L.Control.extend({ options: { position: 'bottomleft' }, onAdd: function () { hud = L.DomUtil.create('div', 'ind-hud'); return hud; } });
    map.addControl(new C());
    drawHud();
    setInterval(function () { if (!document.hidden) drawHud(); }, 1000);
  }

  /* ── 2. Профилът: лист отдолу + снимки с прелистване ── */
  function photoDots() {
    var ph = $('mphotos');
    if (!ph) return;
    var old = ph.nextElementSibling;
    if (old && old.className === 'ind-dots') old.remove();
    var imgs = ph.querySelectorAll('img');
    ph.scrollLeft = 0;
    if (imgs.length < 2) return;
    var dots = document.createElement('div');
    dots.className = 'ind-dots';
    dots.innerHTML = Array.prototype.map.call(imgs, function (_, i) { return '<i' + (i ? '' : ' class="on"') + '></i>'; }).join('');
    ph.parentNode.insertBefore(dots, ph.nextSibling);
    if (!ph.__indBound) {
      ph.__indBound = 1;
      ph.addEventListener('scroll', function () {
        var d = ph.nextElementSibling;
        if (!d || d.className !== 'ind-dots') return;
        var im = ph.querySelectorAll('img'), best = 0, bx = 1e9, mid = ph.scrollLeft + ph.clientWidth / 2;
        Array.prototype.forEach.call(im, function (x, i) { var c = Math.abs(x.offsetLeft + x.offsetWidth / 2 - mid); if (c < bx) { bx = c; best = i; } });
        Array.prototype.forEach.call(d.children, function (x, i) { x.classList.toggle('on', i === best); });
      }, { passive: true });
    }
  }
  wrap('openMod', function (id) {
    var d = byId(id), mb = document.querySelector('#modal .mb');
    if (!d) return;
    var c2 = $('mcar2');
    if (c2) c2.innerHTML = '<span>' + esc(d.car) + '</span>' + plate(d.plate);
    if (mb) { mb.scrollTop = 0; mb.style.transform = ''; }
    photoDots();
    select(id);
    var pm = $('page-map');
    if (pm && pm.classList.contains('on') && !skipFly) flyTo(d);
    skipFly = false;
  });
  wrap('closeMod', function () { select(null); }, function () {
    var m = $('modal');
    if (RM || !m || !m.classList.contains('on') || m.__closing) return true;
    m.__closing = 1;
    m.classList.add('ind-closing');
    setTimeout(function () {
      m.__closing = 0;
      window.closeMod.__orig();
      m.classList.remove('ind-closing');
      var mb = m.querySelector('.mb'); if (mb) mb.style.transform = '';
      select(null);
    }, 230);
    return false;
  });

  /* влачене надолу за затваряне */
  function bindSheetDrag() {
    var mb = document.querySelector('#modal .mb');
    if (!mb || mb.__indDrag) return;
    mb.__indDrag = 1;
    var g = document.createElement('div'); g.className = 'ind-grab'; mb.insertBefore(g, mb.firstChild);
    var y0 = null, x0 = 0, dy = 0, lock = null;
    mb.addEventListener('touchstart', function (e) {
      if (mb.scrollTop > 0 || e.target.closest('#loc-picker-map,.mphotos,select,input')) { y0 = null; return; }
      y0 = e.touches[0].clientY; x0 = e.touches[0].clientX; dy = 0; lock = null;
    }, { passive: true });
    mb.addEventListener('touchmove', function (e) {
      if (y0 === null) return;
      var ddy = e.touches[0].clientY - y0, ddx = e.touches[0].clientX - x0;
      if (lock === null && (Math.abs(ddy) > 6 || Math.abs(ddx) > 6)) lock = Math.abs(ddy) > Math.abs(ddx) && ddy > 0 ? 'y' : 'n';
      if (lock !== 'y') return;
      dy = Math.max(0, ddy);
      e.preventDefault();
      mb.classList.add('ind-drag'); mb.classList.remove('ind-back');
      mb.style.transform = 'translateY(' + dy + 'px)';
    }, { passive: false });
    mb.addEventListener('touchend', function () {
      if (y0 === null) return;
      y0 = null; mb.classList.remove('ind-drag');
      if (lock !== 'y') return;
      if (dy > 110) { buzz(10); closeMod(); }
      else { mb.classList.add('ind-back'); mb.style.transform = ''; }
    });
  }

  /* ── 3. Табове: плъзгаща се черта + преход ── */
  var ORDER = ['map', 'list', 'how', 'reg'], curTab = 'map';
  function moveBar() {
    var on = document.querySelector('.tab.on'), bar = document.querySelector('.ind-tabbar');
    if (!on || !bar) return;
    bar.style.width = on.offsetWidth + 'px';
    bar.style.transform = 'translateX(' + on.offsetLeft + 'px)';
  }
  wrap('showTab', function (t) {
    moveBar();
    var pg = $('page-' + t);
    if (pg && !RM && t !== curTab) {
      var cls = ORDER.indexOf(t) > ORDER.indexOf(curTab) ? 'ind-in-r' : 'ind-in-l';
      pg.classList.remove('ind-in-r', 'ind-in-l'); void pg.offsetWidth; pg.classList.add(cls);
      setTimeout(function () { pg.classList.remove(cls); if (t === 'map' && window.map) map.invalidateSize(); }, 380);
    }
    if (t !== curTab) buzz(5);
    curTab = t;
    if (t === 'reg') spotsCount();
  });

  /* брояч „свободни места“ — веднъж на сесия */
  var spotsDone = false;
  function spotsCount() {
    if (spotsDone || RM) return;
    var el = $('r-spotsleft'), m = el && el.textContent.match(/(\d+)\s*\/\s*(\d+)/);
    if (!m) return;
    spotsDone = true;
    var to = +m[1], from = +m[2], tpl = el.textContent, t0 = performance.now();
    var bar = el.previousElementSibling && el.previousElementSibling.firstElementChild;
    if (bar) { var w = bar.style.width; bar.style.transition = 'none'; bar.style.width = '0'; void bar.offsetWidth; bar.style.transition = 'width 1s cubic-bezier(.2,.9,.25,1)'; bar.style.width = w; }
    (function step(t) {
      var k = Math.min(1, (t - t0) / 1000); k = 1 - Math.pow(1 - k, 3);
      el.textContent = tpl.replace(m[0], Math.round(from + (to - from) * k) + ' / ' + from);
      if (k < 1) requestAnimationFrame(step);
    })(t0);
  }

  /* ── 4. Картите: табела + поява на новите ── */
  var shown = { dlist: {}, 'map-list': {} };
  wrap('render', function () {
    ['dlist', 'map-list'].forEach(function (box) {
      var host = $(box); if (!host) return;
      var now = {}, i = 0;
      Array.prototype.forEach.call(host.querySelectorAll('.dc'), function (dc) {
        var m = (dc.getAttribute('onclick') || '').match(/openMod\((\d+)\)/), d = m && byId(+m[1]);
        if (!d) return;
        now[d.id] = 1;
        dc.classList.add(d.online ? 'ind-on' : 'ind-off');
        var cc = dc.querySelector('.dcc');
        if (cc && !cc.querySelector('.ind-plate')) cc.innerHTML = '<span>' + esc(d.car) + '</span>' + plate(d.plate);
        if (!RM && !shown[box][d.id] && i < 10) {
          dc.style.setProperty('--d', (i * 55) + 'ms');
          dc.classList.add('ind-in');
          dc.addEventListener('animationend', function () { dc.classList.remove('ind-in'); }, { once: true });
        }
        i++;
      });
      shown[box] = now;
    });
  });

  /* ── 5. Отклик: вълна при натиск + вибрация при поръчка ── */
  if (!RM) {
    document.addEventListener('pointerdown', function (e) {
      var b = e.target.closest('button,.flt,.tab,.dc');
      if (!b || b.closest('.leaflet-container')) return;
      var r = b.getBoundingClientRect(), s = Math.max(r.width, r.height) * 2.2;
      if (getComputedStyle(b).position === 'static') b.classList.add('ind-rp');
      else b.style.overflow = b.style.overflow || 'hidden';
      var rp = document.createElement('span');
      rp.className = 'ind-rip';
      rp.style.cssText = 'width:' + s + 'px;height:' + s + 'px;left:' + (e.clientX - r.left - s / 2) + 'px;top:' + (e.clientY - r.top - s / 2) + 'px';
      b.appendChild(rp);
      setTimeout(function () { rp.remove(); }, 600);
    }, { passive: true });
  }
  wrap('orderNowSimple', null, function () { buzz([18, 40, 18]); });
  ['doCall', 'qc'].forEach(function (n) { wrap(n, null, function () { buzz(25); }); });
  ['doVibOrder', 'doWAOrder', 'doSMSOrder', 'qv'].forEach(function (n) { wrap(n, null, function () { buzz([14, 30, 14]); }); });
  wrap('sf', null, function () { buzz(6); });

  /* ── старт: главният скрипт вече е нарисувал всичко веднъж ── */
  function boot() {
    var tabs = $('tabsbar');
    if (tabs && !tabs.querySelector('.ind-tabbar')) { var b = document.createElement('span'); b.className = 'ind-tabbar'; tabs.appendChild(b); }
    moveBar();
    window.addEventListener('resize', moveBar);
    bindSheetDrag();
    if (window.mapReady && window.map) { addHud(); renderMap(); }
    else wrap('initMapOnce', function () { addHud(); renderMap(); });
    if (typeof window.render === 'function') render();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
