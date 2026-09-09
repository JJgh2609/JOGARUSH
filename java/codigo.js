document.addEventListener('DOMContentLoaded', () => {
  const menuBtn = document.getElementById('menuBtn');
  const nav = document.getElementById('mainNav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', () => nav.classList.toggle('open'));
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => nav.classList.remove('open')));
  }

  document.querySelectorAll('.track-social').forEach(link => {
    link.addEventListener('click', () => {
      const platform = link.dataset.platform || 'social';
      if (typeof gtag === 'function') gtag('event', `click_${platform}`, {platform, link_url: link.href});
    });
  });

  document.querySelectorAll('.track-whatsapp').forEach(link => {
    link.addEventListener('click', () => {
      if (typeof gtag === 'function') gtag('event', 'click_whatsapp', {link_url: link.href});
    });
  });

  document.querySelectorAll('.affiliate-link').forEach(link => {
    link.addEventListener('click', e => {
      if (link.getAttribute('href') === '#') { e.preventDefault(); return; }
      if (typeof gtag === 'function') gtag('event', 'click_mercadolibre', {product: link.dataset.product || 'producto', link_url: link.href});
    });
  });
});
