const CACHE = 'sig-sols-v1';
const ASSETS = [
  '/frontend/index.html',
  '/frontend/css/style.css',
  '/frontend/js/api.js',
  '/frontend/manifest.json',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
});

self.addEventListener('fetch', (e) => {
  if (e.request.url.includes('/api/')) return;
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request)),
  );
});
