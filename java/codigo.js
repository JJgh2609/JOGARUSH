document.addEventListener('DOMContentLoaded', () => {

    const menuBtn =
        document.getElementById('menuBtn');

    const nav =
        document.getElementById('mainNav');


    if (menuBtn && nav) {

        menuBtn.addEventListener(
            'click',
            () => nav.classList.toggle('open')
        );


        nav.querySelectorAll('a').forEach(a => {

            a.addEventListener(
                'click',
                () => nav.classList.remove('open')
            );

        });

    }


    document
        .querySelectorAll('.track-social')
        .forEach(link => {

            link.addEventListener('click', () => {

                const platform =
                    link.dataset.platform || 'social';

                if (typeof gtag === 'function') {

                    gtag(
                        'event',
                        `click_${platform}`,
                        {
                            platform,
                            link_url: link.href
                        }
                    );

                }

            });

        });


    document
        .querySelectorAll('.track-whatsapp')
        .forEach(link => {

            link.addEventListener('click', () => {

                if (typeof gtag === 'function') {

                    gtag(
                        'event',
                        'click_whatsapp',
                        {
                            link_url: link.href
                        }
                    );

                }

            });

        });


    document
        .querySelectorAll('.affiliate-link')
        .forEach(link => {

            link.addEventListener(
                'click',
                e => {

                    if (
                        link.getAttribute('href') === '#'
                    ) {
                        e.preventDefault();
                        return;
                    }


                    if (
                        typeof gtag === 'function'
                    ) {

                        gtag(
                            'event',
                            'click_mercadolibre',
                            {
                                product:
                                    link.dataset.product
                                    || 'producto',

                                link_url:
                                    link.href
                            }
                        );

                    }

                }
            );

        });

});


/* =====================================================
   CARGAR TODO DESDE segmentos.json
===================================================== */

async function cargarShortsJogaRush() {

    try {

        const respuesta = await fetch(

            "https://raw.githubusercontent.com/JJgh2609/JOGARUSH/main/data/segmentos.json?t="
            + Date.now(),

            {
                cache: "no-store"
            }

        );


        if (!respuesta.ok) {

            throw new Error(
                "No se pudo leer segmentos.json"
            );

        }


        const datos =
            await respuesta.json();


        cargarUltimosShorts(datos);

        cargarYoutubeDestacados(datos);


    } catch (error) {

        console.error(
            "Error cargando contenido JogaRush:",
            error
        );

    }

}


document.addEventListener(
    "DOMContentLoaded",
    cargarShortsJogaRush
);


/* =====================================================
   LOS 5 SHORTS MÁS RECIENTES
===================================================== */

function cargarUltimosShorts(datos) {

    const contenedor =
        document.getElementById(
            "ultimos-shorts"
        );


    if (!contenedor) {
        return;
    }


    const videos =
        datos.ultimos_shorts;


    if (
        !Array.isArray(videos)
        || videos.length === 0
    ) {

        contenedor.innerHTML =
            "<p>No hay Shorts disponibles en este momento.</p>";

        return;

    }


    const iconos = {
        news: "⚡",
        tips: "💡",
        futbol: "⚽",
        gaming: "🎮",
        cine_anime: "🍿"
    };


    contenedor.innerHTML = "";


    videos
        .slice(0, 5)
        .forEach(video => {


            const tarjeta =
                document.createElement(
                    "article"
                );

            tarjeta.className =
                "segment-card";


            const icono =
                document.createElement(
                    "span"
                );

            icono.className =
                "segment-icon";

            icono.textContent =
                iconos[video.segmento]
                || "🎬";


            const etiqueta =
                document.createElement(
                    "span"
                );

            etiqueta.className =
                "tag";

            etiqueta.textContent =
                video.etiqueta
                || video.segmento;


            const imagen =
                document.createElement(
                    "img"
                );

            imagen.className =
                "segment-thumbnail";

            imagen.src =
                video.miniatura;

            imagen.alt =
                video.titulo;

            imagen.loading =
                "lazy";


            const titulo =
                document.createElement(
                    "h3"
                );

            titulo.className =
                "segment-title";

            titulo.textContent =
                video.titulo;


            const fecha =
                document.createElement(
                    "p"
                );

            fecha.className =
                "segment-date";


            const fechaVideo =
                video.fecha_video
                || video.fecha_playlist;


            if (fechaVideo) {

                fecha.textContent =
                    new Date(
                        fechaVideo
                    ).toLocaleDateString(

                        "es-MX",

                        {
                            day: "2-digit",
                            month: "2-digit",
                            year: "numeric"
                        }

                    );

            }


            const enlace =
                document.createElement(
                    "a"
                );

            enlace.className =
                "btn btn-segment segment-link";

            enlace.href =
                video.url;

            enlace.target =
                "_blank";

            enlace.rel =
                "noopener";

            enlace.textContent =
                "▶ Ver Short";


            enlace.addEventListener(
                "click",
                () => {

                    if (
                        typeof gtag
                        === "function"
                    ) {

                        gtag(
                            "event",
                            "click_segmento_youtube",
                            {
                                segmento:
                                    video.segmento,

                                titulo_video:
                                    video.titulo,

                                video_id:
                                    video.videoId
                            }
                        );

                    }

                }
            );


            tarjeta.appendChild(
                icono
            );

            tarjeta.appendChild(
                etiqueta
            );

            tarjeta.appendChild(
                imagen
            );

            tarjeta.appendChild(
                titulo
            );

            tarjeta.appendChild(
                fecha
            );

            tarjeta.appendChild(
                enlace
            );


            contenedor.appendChild(
                tarjeta
            );

        });

}


/* =====================================================
   YOUTUBE: VIDEOS / LIVES
===================================================== */

function cargarYoutubeDestacados(datos) {

    const videos =
        datos.youtube_destacados;


    if (
        !Array.isArray(videos)
        || videos.length === 0
    ) {

        console.warn(
            "No hay videos destacados disponibles."
        );

        return;

    }


    videos
        .slice(0, 2)
        .forEach(
            (video, indice) => {


                const numero =
                    indice + 1;


                const iframe =
                    document.getElementById(
                        `youtube-video-${numero}`
                    );


                const titulo =
                    document.getElementById(
                        `youtube-title-${numero}`
                    );


                const etiqueta =
                    document.getElementById(
                        `youtube-label-${numero}`
                    );


                if (
                    !iframe
                    || !titulo
                    || !etiqueta
                ) {
                    return;
                }


                iframe.src =
                    video.embed;


                titulo.textContent =
                    video.titulo;


                etiqueta.textContent =
                    video.en_vivo
                        ? "🔴 EN VIVO"
                        : indice === 0
                            ? "MÁS RECIENTE"
                            : "RECIENTE";

            }
        );

}
