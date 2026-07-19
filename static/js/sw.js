/**
 * Marina Gadgets Kano — PWA Service Worker
 * Caches static assets for fast loads and offline support.
 */

const CACHE_NAME = 'marina-v1';
const STATIC_CACHE = 'marina-static-v1';
const DYNAMIC_CACHE = 'marina-dynamic-v1';

// Assets to pre-cache on install (app shell)
const PRECACHE_ASSETS = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/offline/',
];

// Install: pre-cache app shell
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then(cache => {
            return cache.addAll(PRECACHE_ASSETS);
        }).then(() => self.skipWaiting())
    );
});

// Activate: clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys
                    .filter(key => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
                    .map(key => caches.delete(key))
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch strategy:
// - Static assets (CSS, JS, fonts, images): Cache First
// - Pages (HTML): Network First with offline fallback
// - API/AJAX: Network Only
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') return;

    // Skip admin, dashboard, payment, and AJAX endpoints — always network
    const skipPatterns = ['/admin/', '/staff/', '/payment/', '/api/', '/webhook/', '__'];
    if (skipPatterns.some(p => url.pathname.startsWith(p))) return;

    // Static assets — Cache First
    if (url.pathname.startsWith('/static/') || url.hostname !== self.location.hostname) {
        event.respondWith(
            caches.match(request).then(cached => {
                return cached || fetch(request).then(response => {
                    if (response && response.status === 200) {
                        const cloned = response.clone();
                        caches.open(STATIC_CACHE).then(cache => cache.put(request, cloned));
                    }
                    return response;
                });
            })
        );
        return;
    }

    // HTML pages — Network First with offline fallback
    if (request.headers.get('accept') && request.headers.get('accept').includes('text/html')) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    // Cache successful page loads
                    if (response && response.status === 200) {
                        const cloned = response.clone();
                        caches.open(DYNAMIC_CACHE).then(cache => cache.put(request, cloned));
                    }
                    return response;
                })
                .catch(() => {
                    // Network failed — try cache, then offline page
                    return caches.match(request)
                        .then(cached => cached || caches.match('/offline/'));
                })
        );
        return;
    }
});
