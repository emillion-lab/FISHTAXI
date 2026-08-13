// fish.taxi driver API · Cloudflare Worker
//
// Маршрути:
//   POST /v1/register        регистрация (телефон + PIN + кола)
//   POST /v1/login           вход
//   POST /v1/logout          изход
//   GET  /v1/me              профил + текущ достъп
//   POST /v1/online          излизане онлайн в град
//   POST /v1/heartbeat       поддържане на онлайн сесията
//   POST /v1/offline         край на онлайн сесия
//   GET  /v1/cities?cc=BG    градове за държава
//   POST /v1/city-request    заявка за нов град
//
// Достъпът до данни се решава на едно място — accessLevel() отдолу.
// Не разпръсквай тази логика по клиента; клиентът само чете нивото.

import {
  randomHex, hashPin, verifyPin, hashToken,
  normalizePhone, validPin, weakPin
} from './auth.js';

const SESSION_DAYS = 90;
const ONLINE_STALE_SECONDS = 300;   // без heartbeat 5 мин => броим сесията за приключила
const MAX_PIN_ATTEMPTS = 5;
const LOCK_SECONDS = 900;           // 15 мин

const json = (data, status = 200, extra = {}) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors(), ...extra }
  });

const err = (msg, status = 400, code) => json({ error: msg, code }, status);

function cors() {
  return {
    'Access-Control-Allow-Origin': 'https://fish.taxi',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Max-Age': '86400'
  };
}

const now = () => Math.floor(Date.now() / 1000);

async function readJson(req) {
  try { return await req.json(); } catch { return null; }
}

// ─── Сесии ──────────────────────────────────────────────────────────────

async function currentDriver(req, env) {
  const auth = req.headers.get('Authorization') || '';
  const token = auth.startsWith('Bearer ') ? auth.slice(7) : null;
  if (!token) return null;

  const th = await hashToken(token);
  const row = await env.DB.prepare(`
    SELECT d.*, s.token_hash, s.expires_at
      FROM sessions s
      JOIN drivers d ON d.id = s.driver_id
     WHERE s.token_hash = ?1
       AND s.revoked_at IS NULL
       AND s.expires_at > ?2
  `).bind(th, now()).first();

  if (!row) return null;
  await env.DB.prepare('UPDATE drivers SET last_seen_at = ?1 WHERE id = ?2')
    .bind(now(), row.id).run();
  return row;
}

async function issueSession(env, driverId) {
  const token = randomHex(32);
  const th = await hashToken(token);
  const exp = now() + SESSION_DAYS * 86400;
  await env.DB.prepare(
    'INSERT INTO sessions (token_hash, driver_id, expires_at) VALUES (?1, ?2, ?3)'
  ).bind(th, driverId, exp).run();
  return { token, expires_at: exp };
}

// ─── Ниво на достъп ─────────────────────────────────────────────────────
// 'full'  — регистриран и онлайн: всички живи данни
// 'basic' — регистриран, офлайн: зони, история, риск; живите данни са замъглени
// 'demo'  — нерегистриран: замъглено, но с един истински брой за доказателство

async function accessLevel(env, driver) {
  if (!driver) return { level: 'demo', online: false };
  if (driver.status !== 'active') return { level: 'basic', online: false };

  const open = await env.DB.prepare(`
    SELECT id, city_id, heartbeat_at FROM online_sessions
     WHERE driver_id = ?1 AND ended_at IS NULL
     ORDER BY started_at DESC LIMIT 1
  `).bind(driver.id).first();

  if (!open) return { level: 'basic', online: false };

  if (now() - open.heartbeat_at > ONLINE_STALE_SECONDS) {
    await env.DB.prepare('UPDATE online_sessions SET ended_at = ?1 WHERE id = ?2')
      .bind(open.heartbeat_at, open.id).run();
    return { level: 'basic', online: false, note: 'сесията изтече без heartbeat' };
  }

  return { level: 'full', online: true, city_id: open.city_id };
}

// ─── Маршрути ───────────────────────────────────────────────────────────

async function register(req, env) {
  const b = await readJson(req);
  if (!b) return err('невалиден JSON');

  const phone = normalizePhone(b.phone);
  if (!phone) return err('невалиден телефон', 400, 'BAD_PHONE');
  if (!validPin(b.pin)) return err('PIN трябва да е 4–6 цифри', 400, 'BAD_PIN');
  if (weakPin(b.pin)) return err('твърде лесен PIN', 400, 'WEAK_PIN');
  if (!b.name || String(b.name).trim().split(/\s+/).length < 2)
    return err('име и фамилия', 400, 'BAD_NAME');
  if (!b.city_id) return err('липсва град', 400, 'NO_CITY');

  const city = await env.DB.prepare(`
    SELECT c.*, co.verification_mode
      FROM cities c JOIN countries co ON co.code = c.country_code
     WHERE c.id = ?1
  `).bind(b.city_id).first();
  if (!city) return err('непознат град', 404, 'NO_CITY');

  const exists = await env.DB.prepare('SELECT id FROM drivers WHERE phone = ?1')
    .bind(phone).first();
  if (exists) return err('този телефон вече е регистриран', 409, 'PHONE_TAKEN');

  // Режимът се заковава сега — ако утре добавим регистър за CH,
  // старите записи не се преправят задна дата.
  const mode = city.verification_mode;
  if (mode === 'registry' && !b.registry_ref)
    return err('за България изберете кола от регистъра', 400, 'NEED_REGISTRY_PICK');
  if (mode === 'trust' && !b.plate)
    return err('въведете регистрационен номер', 400, 'NEED_PLATE');

  const { hash, salt } = await hashPin(b.pin);

  const d = await env.DB.prepare(`
    INSERT INTO drivers (phone, pin_hash, pin_salt, name, lang_pref, home_city_id, status)
    VALUES (?1, ?2, ?3, ?4, ?5, ?6, 'pending')
    RETURNING id
  `).bind(phone, hash, salt, String(b.name).trim(), b.lang || null, city.id).first();

  await env.DB.prepare(`
    INSERT INTO vehicles
      (driver_id, plate, make_model, first_reg_year, operator_name,
       verification_mode, registry_ref, licence_valid_to, review_status)
    VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9)
  `).bind(
    d.id,
    String(b.plate || '').toUpperCase().replace(/\s/g, ''),
    b.make_model || null,
    b.first_reg_year || null,
    b.operator_name || null,
    mode,
    b.registry_ref || null,
    b.licence_valid_to || null,
    mode === 'registry' ? 'approved' : 'pending'
  ).run();

  // При регистър проверката е автоматична; при доверие чака ръчен преглед.
  if (mode === 'registry') {
    await env.DB.prepare("UPDATE drivers SET status = 'active' WHERE id = ?1")
      .bind(d.id).run();
  }

  const s = await issueSession(env, d.id);
  return json({
    ok: true,
    driver_id: d.id,
    verification_mode: mode,
    status: mode === 'registry' ? 'active' : 'pending',
    token: s.token,
    expires_at: s.expires_at
  }, 201);
}

async function login(req, env) {
  const b = await readJson(req);
  if (!b) return err('невалиден JSON');

  const phone = normalizePhone(b.phone);
  if (!phone || !validPin(b.pin)) return err('грешен телефон или PIN', 401, 'BAD_CREDS');

  const d = await env.DB.prepare('SELECT * FROM drivers WHERE phone = ?1')
    .bind(phone).first();

  // Един и същ отговор при липсващ шофьор и при грешен PIN —
  // за да не може да се проверява кои телефони са регистрирани.
  if (!d) return err('грешен телефон или PIN', 401, 'BAD_CREDS');

  if (d.locked_until && d.locked_until > now())
    return err('твърде много опити, опитайте по-късно', 429, 'LOCKED');

  const ok = await verifyPin(b.pin, d.pin_salt, d.pin_hash);
  if (!ok) {
    const fails = (d.failed_pins || 0) + 1;
    const lock = fails >= MAX_PIN_ATTEMPTS ? now() + LOCK_SECONDS : null;
    await env.DB.prepare(
      'UPDATE drivers SET failed_pins = ?1, locked_until = ?2 WHERE id = ?3'
    ).bind(lock ? 0 : fails, lock, d.id).run();
    return err('грешен телефон или PIN', 401, 'BAD_CREDS');
  }

  await env.DB.prepare(
    'UPDATE drivers SET failed_pins = 0, locked_until = NULL WHERE id = ?1'
  ).bind(d.id).run();

  const s = await issueSession(env, d.id);
  return json({ ok: true, token: s.token, expires_at: s.expires_at, status: d.status });
}

async function logout(req, env) {
  const auth = req.headers.get('Authorization') || '';
  const token = auth.startsWith('Bearer ') ? auth.slice(7) : null;
  if (token) {
    await env.DB.prepare(
      'UPDATE sessions SET revoked_at = ?1 WHERE token_hash = ?2'
    ).bind(now(), await hashToken(token)).run();
  }
  return json({ ok: true });
}

async function me(req, env) {
  const d = await currentDriver(req, env);
  if (!d) return json({ level: 'demo', authenticated: false });

  const access = await accessLevel(env, d);
  const v = await env.DB.prepare(
    'SELECT plate, make_model, verification_mode, review_status FROM vehicles WHERE driver_id = ?1'
  ).bind(d.id).all();

  return json({
    authenticated: true,
    driver: {
      id: d.id, name: d.name, phone: d.phone,
      status: d.status, lang: d.lang_pref,
      home_city_id: d.home_city_id, founder_no: d.founder_no
    },
    vehicles: v.results || [],
    access
  });
}

async function goOnline(req, env) {
  const d = await currentDriver(req, env);
  if (!d) return err('нужен е вход', 401, 'NO_AUTH');
  if (d.status !== 'active') return err('профилът още се проверява', 403, 'PENDING');

  const b = await readJson(req) || {};
  const cityId = b.city_id || d.home_city_id;
  if (!cityId) return err('липсва град', 400, 'NO_CITY');

  const city = await env.DB.prepare("SELECT id, status FROM cities WHERE id = ?1")
    .bind(cityId).first();
  if (!city) return err('непознат град', 404, 'NO_CITY');
  if (city.status !== 'live') return err('градът още не е активен', 409, 'CITY_NOT_LIVE');

  const open = await env.DB.prepare(
    'SELECT id FROM online_sessions WHERE driver_id = ?1 AND ended_at IS NULL'
  ).bind(d.id).first();

  if (open) {
    await env.DB.prepare('UPDATE online_sessions SET heartbeat_at = ?1 WHERE id = ?2')
      .bind(now(), open.id).run();
    return json({ ok: true, session_id: open.id, resumed: true });
  }

  const s = await env.DB.prepare(
    'INSERT INTO online_sessions (driver_id, city_id) VALUES (?1, ?2) RETURNING id'
  ).bind(d.id, cityId).first();

  return json({ ok: true, session_id: s.id, resumed: false });
}

async function heartbeat(req, env) {
  const d = await currentDriver(req, env);
  if (!d) return err('нужен е вход', 401, 'NO_AUTH');
  const r = await env.DB.prepare(`
    UPDATE online_sessions SET heartbeat_at = ?1
     WHERE driver_id = ?2 AND ended_at IS NULL
  `).bind(now(), d.id).run();
  return json({ ok: true, updated: r.meta?.changes || 0 });
}

async function goOffline(req, env) {
  const d = await currentDriver(req, env);
  if (!d) return err('нужен е вход', 401, 'NO_AUTH');
  await env.DB.prepare(`
    UPDATE online_sessions SET ended_at = ?1
     WHERE driver_id = ?2 AND ended_at IS NULL
  `).bind(now(), d.id).run();
  return json({ ok: true });
}

async function listCities(req, env) {
  const url = new URL(req.url);
  const cc = url.searchParams.get('cc');
  const q = cc
    ? env.DB.prepare(`
        SELECT id, country_code, slug, name, name_local, lang_default, tz, status
          FROM cities WHERE country_code = ?1 ORDER BY status = 'live' DESC, name
      `).bind(cc)
    : env.DB.prepare(`
        SELECT id, country_code, slug, name, name_local, lang_default, tz, status
          FROM cities ORDER BY country_code, name
      `);
  const r = await q.all();
  return json({ cities: r.results || [] });
}

async function listCountries(req, env) {
  const r = await env.DB.prepare(
    'SELECT code, name, currency, verification_mode FROM countries ORDER BY name'
  ).all();
  return json({ countries: r.results || [] });
}

async function cityRequest(req, env) {
  const b = await readJson(req);
  if (!b || !b.city_name || !b.country_code)
    return err('нужни са държава и град', 400, 'BAD_INPUT');

  const d = await currentDriver(req, env);   // може и без вход — заявката е сигнал
  const name = String(b.city_name).trim();

  const existing = await env.DB.prepare(`
    SELECT id, status, city_id FROM city_requests
     WHERE country_code = ?1 AND lower(city_name) = lower(?2)
     ORDER BY created_at DESC LIMIT 1
  `).bind(b.country_code, name).first();

  if (existing) {
    const cnt = await env.DB.prepare(`
      SELECT COUNT(*) AS n FROM city_requests
       WHERE country_code = ?1 AND lower(city_name) = lower(?2)
    `).bind(b.country_code, name).first();
    // Записваме и повторната заявка — броят е сигналът за приоритет.
    await env.DB.prepare(`
      INSERT INTO city_requests (driver_id, country_code, city_name, note)
      VALUES (?1, ?2, ?3, ?4)
    `).bind(d?.id || null, b.country_code, name, b.note || null).run();
    return json({ ok: true, status: existing.status, requests: (cnt?.n || 0) + 1 });
  }

  await env.DB.prepare(`
    INSERT INTO city_requests (driver_id, country_code, city_name, note)
    VALUES (?1, ?2, ?3, ?4)
  `).bind(d?.id || null, b.country_code, name, b.note || null).run();

  return json({ ok: true, status: 'requested', requests: 1 }, 201);
}

// ─── Вход ───────────────────────────────────────────────────────────────

export default {
  async fetch(req, env) {
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors() });

    const url = new URL(req.url);
    const p = url.pathname;
    const m = req.method;

    try {
      if (m === 'POST' && p === '/v1/register')     return await register(req, env);
      if (m === 'POST' && p === '/v1/login')        return await login(req, env);
      if (m === 'POST' && p === '/v1/logout')       return await logout(req, env);
      if (m === 'GET'  && p === '/v1/me')           return await me(req, env);
      if (m === 'POST' && p === '/v1/online')       return await goOnline(req, env);
      if (m === 'POST' && p === '/v1/heartbeat')    return await heartbeat(req, env);
      if (m === 'POST' && p === '/v1/offline')      return await goOffline(req, env);
      if (m === 'GET'  && p === '/v1/cities')       return await listCities(req, env);
      if (m === 'GET'  && p === '/v1/countries')    return await listCountries(req, env);
      if (m === 'POST' && p === '/v1/city-request') return await cityRequest(req, env);
      if (m === 'GET'  && p === '/v1/health')       return json({ ok: true, ts: now() });

      return err('няма такъв маршрут', 404, 'NO_ROUTE');
    } catch (e) {
      console.error('unhandled', e);
      return err('вътрешна грешка', 500, 'INTERNAL');
    }
  }
};
