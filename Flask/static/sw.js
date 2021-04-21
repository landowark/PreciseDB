importScripts("/static/js/db_stores.js")

CACHE_NAME = "test-cache-v1";
CACHE_URLS = [ '/static/css/page.css', '/', '/sw.js' ];

self.addEventListener("fetch", function(event) {
    console.log("Fetch event registered.")
    event.respondWith(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.match(event.request).then(function(cachedResponse) {
                var fetchPromise = fetch(event.request).then(function(networkResponse) {
                    cache.put(event.request, networkResponse.clone());
                    return networkResponse;
                });
                return cachedResponse || fetchPromise;
            })
        })
    );
});

self.addEventListener("install", function(event) {
    openDatabase();
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(CACHE_URLS);
        })
    );
});

self.addEventListener("sync", function(event) {
    console.log("Sync event registered.")
    if (event.tag == "namesSync") {
        console.log("namesSync has been called!");
        event.waitUntil(syncNames());
    }
});