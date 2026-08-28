// Morgenlog service worker
// Bemærk: denne cache rører ALDRIG localStorage. Dine loggede pas, morgental
// og din plan ligger et helt andet sted og bliver hverken slettet eller rørt,
// når appen opdateres.

const CACHE = "morgenlog-v2";
const FILER = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-maskable.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => Promise.allSettled(FILER.map((f) => c.add(f))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((n) => Promise.all(n.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Netværk først, cache som reserve: du får altid nyeste version når du har
// forbindelse, og appen virker stadig i kælderen eller på flytilstand.
// Kald til Anthropic går aldrig gennem cachen.
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;
  e.respondWith(
    fetch(e.request)
      .then((svar) => {
        const kopi = svar.clone();
        caches.open(CACHE).then((c) => c.put(e.request, kopi)).catch(() => {});
        return svar;
      })
      .catch(() => caches.match(e.request).then((r) => r || caches.match("./index.html")))
  );
});
