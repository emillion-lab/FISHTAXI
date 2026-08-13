-- fish.taxi driver backend · D1 схема v1
-- Принцип: градът е ред в таблица, не форк на репо.
-- Принцип: начинът на проверка се чете от държавата, не е зашит в кода.

PRAGMA foreign_keys = ON;

-- ─── География ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS countries (
  code              TEXT PRIMARY KEY,           -- ISO 3166-1 alpha-2: BG, CH, DE
  name              TEXT NOT NULL,
  currency          TEXT NOT NULL,              -- BGN, CHF, EUR
  verification_mode TEXT NOT NULL               -- 'registry' | 'trust'
                    CHECK (verification_mode IN ('registry','trust')),
  registry_source   TEXT,                       -- напр. 'taxireg.infosys.bg'; NULL при trust
  created_at        INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS cities (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  country_code  TEXT NOT NULL REFERENCES countries(code),
  slug          TEXT NOT NULL,                  -- 'sofia', 'zurich', 'winterthur'
  name          TEXT NOT NULL,
  name_local    TEXT,                           -- 'София', 'Zürich'
  lang_default  TEXT NOT NULL,                  -- предложение, не заключване
  tz            TEXT NOT NULL,                  -- 'Europe/Sofia'
  lat           REAL,
  lon           REAL,
  status        TEXT NOT NULL DEFAULT 'requested'
                CHECK (status IN ('requested','building','live','paused')),
  config_json   TEXT,                           -- зони, летище, гара, източници
  created_at    INTEGER NOT NULL DEFAULT (unixepoch()),
  live_at       INTEGER,
  UNIQUE (country_code, slug)
);

CREATE INDEX IF NOT EXISTS idx_cities_status ON cities(status);

-- ─── Шофьори ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS drivers (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  phone         TEXT NOT NULL UNIQUE,           -- нормализиран E.164: +359889...
  pin_hash      TEXT NOT NULL,                  -- PBKDF2-SHA256, виж auth.js
  pin_salt      TEXT NOT NULL,
  name          TEXT NOT NULL,
  lang_pref     TEXT,                           -- NULL => пада към cities.lang_default
  home_city_id  INTEGER REFERENCES cities(id),
  founder_no    INTEGER UNIQUE,                 -- NULL ако не е Founder
  status        TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','active','suspended')),
  failed_pins   INTEGER NOT NULL DEFAULT 0,
  locked_until  INTEGER,                        -- unix ts; защита срещу brute force на 4-цифрен PIN
  created_at    INTEGER NOT NULL DEFAULT (unixepoch()),
  last_seen_at  INTEGER
);

CREATE INDEX IF NOT EXISTS idx_drivers_city ON drivers(home_city_id);

-- ─── Автомобили ───────────────────────────────────────────────────────────
-- verification_mode се копира от countries към момента на регистрация,
-- за да не се преписва задна дата, ако държавата смени режим.

CREATE TABLE IF NOT EXISTS vehicles (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  driver_id         INTEGER NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
  plate             TEXT NOT NULL,
  make_model        TEXT,
  first_reg_year    INTEGER,
  operator_name     TEXT,
  verification_mode TEXT NOT NULL
                    CHECK (verification_mode IN ('registry','trust')),
  registry_ref      TEXT,                       -- taxiOperatorLicenseId при registry
  licence_valid_to  TEXT,                       -- ISO дата от регистъра
  photo_car_url     TEXT,                       -- R2 ключ
  photo_doc_url     TEXT,
  review_status     TEXT NOT NULL DEFAULT 'pending'
                    CHECK (review_status IN ('pending','approved','rejected')),
  review_note       TEXT,
  created_at        INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE INDEX IF NOT EXISTS idx_vehicles_driver ON vehicles(driver_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_review ON vehicles(review_status);

-- ─── Сесии ────────────────────────────────────────────────────────────────
-- Непрозрачен токен в D1, не JWT — за да може да се отнеме моментално.

CREATE TABLE IF NOT EXISTS sessions (
  token_hash  TEXT PRIMARY KEY,                 -- SHA-256 на токена, не самият токен
  driver_id   INTEGER NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
  device_id   INTEGER REFERENCES devices(id) ON DELETE SET NULL,
  created_at  INTEGER NOT NULL DEFAULT (unixepoch()),
  expires_at  INTEGER NOT NULL,
  revoked_at  INTEGER
);

CREATE INDEX IF NOT EXISTS idx_sessions_driver ON sessions(driver_id);

CREATE TABLE IF NOT EXISTS devices (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  driver_id    INTEGER REFERENCES drivers(id) ON DELETE CASCADE,
  fingerprint  TEXT NOT NULL,
  platform     TEXT,
  first_seen   INTEGER NOT NULL DEFAULT (unixepoch()),
  last_seen    INTEGER,
  UNIQUE (driver_id, fingerprint)
);

-- ─── Онлайн статус ────────────────────────────────────────────────────────
-- Отворена сесия = ended_at IS NULL. Оттук се смята правото на пълни данни.

CREATE TABLE IF NOT EXISTS online_sessions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  driver_id   INTEGER NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
  city_id     INTEGER NOT NULL REFERENCES cities(id),
  started_at  INTEGER NOT NULL DEFAULT (unixepoch()),
  ended_at    INTEGER,
  heartbeat_at INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE INDEX IF NOT EXISTS idx_online_open
  ON online_sessions(driver_id) WHERE ended_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_online_city ON online_sessions(city_id, started_at);

-- ─── Заявки за нов град ───────────────────────────────────────────────────
-- Безплатен сигнал за търсене: строим по брой заявки, не по усет.

CREATE TABLE IF NOT EXISTS city_requests (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  driver_id     INTEGER REFERENCES drivers(id) ON DELETE SET NULL,
  country_code  TEXT NOT NULL REFERENCES countries(code),
  city_name     TEXT NOT NULL,
  note          TEXT,
  status        TEXT NOT NULL DEFAULT 'requested'
                CHECK (status IN ('requested','building','live','declined')),
  city_id       INTEGER REFERENCES cities(id),  -- попълва се щом градът се създаде
  created_at    INTEGER NOT NULL DEFAULT (unixepoch()),
  updated_at    INTEGER
);

CREATE INDEX IF NOT EXISTS idx_city_requests_open
  ON city_requests(country_code, city_name) WHERE status = 'requested';

-- ─── Начални данни ────────────────────────────────────────────────────────

INSERT OR IGNORE INTO countries (code, name, currency, verification_mode, registry_source)
VALUES
  ('BG', 'България',   'BGN', 'registry', 'taxireg.infosys.bg'),
  ('CH', 'Schweiz',    'CHF', 'trust',    NULL),
  ('DE', 'Deutschland','EUR', 'trust',    NULL),
  ('AT', 'Österreich', 'EUR', 'trust',    NULL);

INSERT OR IGNORE INTO cities (country_code, slug, name, name_local, lang_default, tz, lat, lon, status)
VALUES
  ('BG', 'sofia',      'Sofia',      'София',      'bg', 'Europe/Sofia',  42.6977, 23.3219, 'live'),
  ('CH', 'zurich',     'Zurich',     'Zürich',     'de', 'Europe/Zurich', 47.3769,  8.5417, 'building'),
  ('CH', 'winterthur', 'Winterthur', 'Winterthur', 'de', 'Europe/Zurich', 47.5001,  8.7241, 'requested');
