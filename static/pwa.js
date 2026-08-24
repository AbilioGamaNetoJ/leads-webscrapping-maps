// Registro do service worker e fluxo de instalação do PWA (Android/desktop via
// `beforeinstallprompt`; iOS Safari não dispara esse evento, então mostramos instruções).
(function () {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js').catch(function () {
        // Falha silenciosa: o app continua funcionando normalmente sem PWA/offline.
      });
    });
  }

  const installBtn = document.getElementById('installAppBtn');
  const iosHint = document.getElementById('iosInstallHint');
  const iosHintClose = document.getElementById('iosInstallHintClose');
  let deferredPrompt = null;

  const isStandalone =
    window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

  const isIos = /iphone|ipad|ipod/i.test(window.navigator.userAgent) && !window.MSStream;

  if (isStandalone) {
    // Já instalado — nada para oferecer.
  } else if (isIos) {
    if (installBtn) installBtn.classList.remove('hidden');
  }

  window.addEventListener('beforeinstallprompt', function (event) {
    event.preventDefault();
    deferredPrompt = event;
    if (installBtn) installBtn.classList.remove('hidden');
  });

  if (installBtn) {
    installBtn.addEventListener('click', async function () {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        await deferredPrompt.userChoice;
        deferredPrompt = null;
        installBtn.classList.add('hidden');
        return;
      }
      if (isIos && iosHint) {
        iosHint.classList.remove('hidden');
      }
    });
  }

  if (iosHintClose && iosHint) {
    iosHintClose.addEventListener('click', function () {
      iosHint.classList.add('hidden');
    });
  }

  window.addEventListener('appinstalled', function () {
    if (installBtn) installBtn.classList.add('hidden');
  });
})();
