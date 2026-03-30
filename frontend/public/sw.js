// 智农兴乡 Service Worker
// Provides offline support for AI Doctor history records and app shell.

const CACHE_NAME = "zhinong-v1";
const OFFLINE_URL = "/offline.html";

// App shell resources to precache
const PRECACHE_URLS = [
  "/",
  "/ai-doctor",
  "/policy",
  "/dashboard",
  "/farmland",
  "/manifest.webmanifest",
  "/offline.html",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
];

// Install: precache app shell
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS)).then(() => self.skipWaiting())
  );
});

// Activate: delete old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
        )
      )
      .then(() => self.clients.claim())
  );
});

// Fetch strategy:
// - API diagnosis records (/api/v1/ai-doctor/records): cache-first (offline support)
// - Navigation requests: network-first, fallback to cache
// - Static assets: cache-first
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Skip non-GET and cross-origin (except our own API)
  if (event.request.method !== "GET") return;

  // AI Doctor records: cache-first for offline support
  if (url.pathname.includes("/api/v1/ai-doctor/records")) {
    event.respondWith(
      caches.open(CACHE_NAME).then(async (cache) => {
        const cached = await cache.match(event.request);
        const fetchPromise = fetch(event.request)
          .then((res) => {
            if (res.ok) cache.put(event.request, res.clone());
            return res;
          })
          .catch(() => cached);
        return cached || fetchPromise;
      })
    );
    return;
  }

  // API calls (other than records): network-only, don't cache
  if (url.pathname.startsWith("/api/")) return;

  // Navigation requests: network-first, fallback to cached page or offline page
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(event.request, clone));
          return res;
        })
        .catch(async () => {
          const cached = await caches.match(event.request);
          return (
            cached ||
            caches.match(OFFLINE_URL) ||
            new Response("离线状态，请检查网络连接", {
              status: 503,
              headers: { "Content-Type": "text/plain; charset=utf-8" },
            })
          );
        })
    );
    return;
  }

  // Static assets (JS, CSS, fonts, images): cache-first
  event.respondWith(
    caches.match(event.request).then(
      (cached) =>
        cached ||
        fetch(event.request).then((res) => {
          if (res.ok) {
            caches.open(CACHE_NAME).then((c) => c.put(event.request, res.clone()));
          }
          return res;
        })
    )
  );
});
