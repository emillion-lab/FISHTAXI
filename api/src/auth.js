// fish.taxi · auth помощни функции за Cloudflare Workers
//
// Защо PBKDF2, а не bcrypt/scrypt: Workers нямат нативен bcrypt, а чист JS
// вариант е бавен и хапе CPU лимита. WebCrypto PBKDF2 е вграден и бърз.
//
// Важно: PIN-ът е 4-6 цифри, тоест слаба тайна по дефиниция. Хешът сам по
// себе си не стига — защитата е в заключването след N грешни опита
// (drivers.failed_pins / locked_until). Не махай едното заради другото.

const PBKDF2_ITERATIONS = 210000;
const KEY_BITS = 256;

const enc = new TextEncoder();

function toHex(buf) {
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
}

function fromHex(hex) {
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.substr(i * 2, 2), 16);
  return out;
}

export function randomHex(bytes = 32) {
  return toHex(crypto.getRandomValues(new Uint8Array(bytes)));
}

export async function hashPin(pin, saltHex) {
  const salt = saltHex ? fromHex(saltHex) : crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.importKey('raw', enc.encode(pin), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', hash: 'SHA-256', salt, iterations: PBKDF2_ITERATIONS },
    key,
    KEY_BITS
  );
  return { hash: toHex(bits), salt: toHex(salt) };
}

// Сравнение в постоянно време — за да не изтича информация през времето за отговор.
export function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export async function verifyPin(pin, saltHex, expectedHash) {
  const { hash } = await hashPin(pin, saltHex);
  return timingSafeEqual(hash, expectedHash);
}

// В базата пазим само SHA-256 на токена. Ако някой прочете таблицата,
// не може да се представи за шофьора.
export async function hashToken(token) {
  return toHex(await crypto.subtle.digest('SHA-256', enc.encode(token)));
}

// Нормализация към E.164. Приема 0888..., 359888..., +359888...
export function normalizePhone(raw, defaultCc = '359') {
  let d = String(raw || '').replace(/\D/g, '');
  if (!d) return null;
  if (d.startsWith('00')) d = d.slice(2);
  if (d.startsWith('0')) d = defaultCc + d.slice(1);
  if (d.length < 8 || d.length > 15) return null;
  return '+' + d;
}

export function validPin(pin) {
  return /^\d{4,6}$/.test(String(pin || ''));
}

// Тривиалните PIN-ове са по-опасни от липсата на PIN, защото дават
// фалшиво усещане за защита. Отхвърляме ги при регистрация.
const WEAK_PINS = new Set([
  '0000','1111','2222','3333','4444','5555','6666','7777','8888','9999',
  '1234','4321','2580','0123','1212','1122','6969','1004','2000','1010'
]);

export function weakPin(pin) {
  return WEAK_PINS.has(String(pin));
}
