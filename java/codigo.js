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

async function cargarShortsJogaRush() {

    try {

        const respuesta = await fetch(
            "data/segmentos.json?v=" + Date.now()
        );

        if (!respuesta.ok) {
            throw new Error("No se pudo leer segmentos.json");
        }

        const datos = await respuesta.json();

        const segmentos = {
            news: "segment-news",
            tips: "segment-tips",
            futbol: "segment-futbol",
            gaming: "segment-gaming",
            cine_anime: "segment-cine_anime"
        };

        Object.entries(segmentos).forEach(([nombre, id]) => {

            const video = datos[nombre];
            const tarjeta = document.getElementById(id);

            if (!tarjeta || !video || video.error) {
                return;
            }

            const imagen = tarjeta.querySelector(".segment-thumbnail");
            const titulo = tarjeta.querySelector(".segment-title");
            const fecha = tarjeta.querySelector(".segment-date");
            const enlace = tarjeta.querySelector(".segment-link");

            imagen.src = video.miniatura;
            titulo.textContent = video.titulo;
            enlace.href = video.url;

            const fechaVideo =
                video.fecha_video ||
                video.fecha_playlist;

            if (fechaVideo) {

                fecha.textContent =
                    new Date(fechaVideo).toLocaleDateString(
                        "es-MX",
                        {
                            day: "2-digit",
                            month: "2-digit",
                            year: "numeric"
                        }
                    );
            }

            enlace.addEventListener("click", () => {

                if (typeof gtag === "function") {

                    gtag("event", "click_segmento_youtube", {
                        segmento: nombre,
                        titulo_video: video.titulo,
                        video_id: video.videoId
                    });

                }

            });

        });

    } catch (error) {

        console.error(
            "Error cargando Shorts JogaRush:",
            error
        );

    }

}

document.addEventListener(
    "DOMContentLoaded",
    cargarShortsJogaRush
);