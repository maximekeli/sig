const CACHE = 'sig-sols-v2';
const ASSETS = [
  '/frontend/index.html',
  '/frontend/css/style.css',
  '/frontend/css/enhancements.css',
  '/frontend/js/init.js',
  '/frontend/js/api.js',
  '/frontend/js/auth.js',
  '/frontend/js/features.js',
  '/frontend/js/map.js',
  '/frontend/js/dashboard.js',
  '/frontend/js/quiz.js',
  '/frontend/js/tools.js',
  '/frontend/js/app.js',
  '/frontend/js/core/toast.js',
  '/frontend/js/core/i18n.js',
  '/frontend/js/core/theme.js',
  '/frontend/js/core/ui.js',
  '/frontend/manifest.json',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))),
    ).then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (e) => {
  const url = e.request.url;
  if (url.includes('/api/')) return;
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then((cached) => {
      const fetched = fetch(e.request).then((res) => {
        if (res.ok && url.includes('/frontend/')) {
          const clone = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, clone));
        }
        return res;
      });
      return cached || fetched;
    }),
  );
});
