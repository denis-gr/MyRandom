importScripts("https://cdn.jsdelivr.net/npm/workbox-sw@6.0.2/build/workbox-sw.min.js");

const ignoreQueryStringPlugin = {
    cachedResponseWillBeUsed: async({request, cachedResponse}) =>
        cachedResponse || caches.match(request.url, {ignoreSearch: true})
};

workbox.routing.registerRoute(
    () => true,
    new workbox.strategies.StaleWhileRevalidate({
        plugins: [
            new workbox.cacheableResponse.CacheableResponsePlugin({
                statuses: [0, 200]
            }),
            ignoreQueryStringPlugin
        ]
    })
);

workbox.precaching.precacheAndRoute([
    'https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.min.js',
    'https://cdn.jsdelivr.net/npm/vue@2/dist/vue.min.js',
    'https://cdn.jsdelivr.net/npm/vue-i18n@8.22.4/dist/vue-i18n.min.js',
    '{{ start_url }}/numbers.html',
    '{{ start_url }}/index.html',
    '{{ start_url }}/names.html',
    '{{ start_url }}/passwords.html',
    '{{ start_url }}/person.html',
    '{{ start_url }}/words.html',
    '{{ start_url }}/list.html',
    '{{ start_url }}/about.html',
], {
    ignoreURLParametersMatching: [/.*/]
});
