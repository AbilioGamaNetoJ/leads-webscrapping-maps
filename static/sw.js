// Service worker do Prospector — Codex Create.
//
// Regra central: nunca cachear rotas com dados de leads ou sessão (/search, /historico,
// /export, /admin/*, /auth/*, /login). O banco é compartilhado entre usuários da equipe;
// um lead ou uma resposta de sessão gravados no cache do disco reapareceriam para outra
// pessoa no mesmo aparelho. Só o "shell" estático (CSS, JS, ícones) e a página /offline
// são pré-cacheados e servidos do cache.

const CACHE_VERSION = 'prospector-v1';

const PRECACHE_URLS = [
  '/static/app.css',
  '/static/app.js',
  '/static/pwa.js',
  '/static/logotipo-fundo-light.png',
  '/static/logotipo-fundo-dark.png',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/icon-maskable-512.png',
  '/static/icons/apple-touch-icon-180.png',
  '/offline',
];

// Prefixos que nunca devem ser servidos ou gravados em cache, mesmo em navegação.
const NEVER_CACHE_PREFIXES = [
  '/search',
  '/historico',
  '/export',
  '/admin',
  '/auth',
  '/login',
  '/logout',
  '/autocomplete',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(PRECACHE_URLS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_VERSION).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

function isNeverCache(pathname) {
  return NEVER_CACHE_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`) || pathname.startsWith(`${prefix}?`));
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (isNeverCache(url.pathname)) return; // deixa passar direto pra rede, sem tocar no cache

  // Navegação de página inteira: tenta a rede primeiro (conteúdo sempre atual quando
  // online); se falhar, cai para a página /offline pré-cacheada.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match('/offline'))
    );
    return;
  }

  // Assets estáticos: cache-first, com atualização em segundo plano (stale-while-revalidate).
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const network = fetch(request)
          .then((response) => {
            if (response.ok) {
              caches.open(CACHE_VERSION).then((cache) => cache.put(request, response.clone()));
            }
            return response;
          })
          .catch(() => cached);
        return cached || network;
      })
    );
  }
});
