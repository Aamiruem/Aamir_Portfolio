/* Aamir Hussain Azad portfolio - service worker (offline + installable) */
var CACHE='aamir-portfolio-v1';
var CORE=['/','/site.webmanifest','/favicon.svg','/icon-192.png','/icon-512.png','/apple-touch-icon.png'];
self.addEventListener('install',function(e){ e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(CORE); }).then(function(){ return self.skipWaiting(); })); });
self.addEventListener('activate',function(e){ e.waitUntil(caches.keys().then(function(ks){ return Promise.all(ks.filter(function(k){ return k!==CACHE; }).map(function(k){ return caches.delete(k); })); }).then(function(){ return self.clients.claim(); })); });
self.addEventListener('fetch',function(e){
  var r=e.request; if(r.method!=='GET') return;
  var u=new URL(r.url); if(u.origin!==location.origin) return;
  if(r.mode==='navigate'){ e.respondWith(fetch(r).then(function(res){ var cp=res.clone(); caches.open(CACHE).then(function(c){ c.put(r,cp); }); return res; }).catch(function(){ return caches.match(r).then(function(m){ return m||caches.match('/'); }); })); return; }
  e.respondWith(caches.match(r).then(function(m){ return m||fetch(r).then(function(res){ if(res.ok&&/\.(png|svg|webp|jpg|ico|webmanifest)$/.test(u.pathname)){ var cp=res.clone(); caches.open(CACHE).then(function(c){ c.put(r,cp); }); } return res; }); }));
});
