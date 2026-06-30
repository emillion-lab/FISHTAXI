// Minimal service worker - required for PWA installability
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => self.clients.claim());
self.addEventListener('fetch', e => {
  // Pass-through, no caching for now (keeps content always fresh)
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
