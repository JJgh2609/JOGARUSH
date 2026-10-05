import os
import re
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_KEY = os.environ["YOUTUBE_API_KEY"]
CHANNEL_HANDLE = "JogaRush"

PLAYLISTS = {
    "news": "PLfFb-ddywg-c",
    "tips": "PLUXoJshp-aP0",
    "futbol": "PLaPVD_LX9Q-w",
    "gaming": "PLSkijo2yWyuw",
    "cine_anime": "PLbo7JjRu4tCI"
}


def api_get(recurso, params):
    params["key"] = API_KEY
    url = (
        f"https://www.googleapis.com/youtube/v3/{recurso}?"
        + urllib.parse.urlencode(params)
    )

    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


# =========================================================
# SHORTS POR PROGRAMA
# =========================================================

def obtener_todos_items(playlist_id):
    items = []
    page_token = None

    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50
        }

        if page_token:
            params["pageToken"] = page_token

        data = api_get("playlistItems", params)
        items.extend(data.get("items", []))

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return items


def fecha_para_ordenar(item):
    content = item.get("contentDetails", {})
    snippet = item.get("snippet", {})

    return (
        content.get("videoPublishedAt")
        or snippet.get("publishedAt")
        or ""
    )


def ultimo_video_playlist(playlist_id):
    items = obtener_todos_items(playlist_id)
    validos = []

    for item in items:
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})

        video_id = (
            content.get("videoId")
            or snippet.get("resourceId", {}).get("videoId")
        )

        titulo = snippet.get("title", "")

        if not video_id:
            continue

        if titulo in ("Deleted video", "Private video"):
            continue

        validos.append(item)

    if not validos:
        return None

    item = max(validos, key=fecha_para_ordenar)

    snippet = item.get("snippet", {})
    content = item.get("contentDetails", {})

    video_id = (
        content.get("videoId")
        or snippet.get("resourceId", {}).get("videoId")
    )

    thumbs = snippet.get("thumbnails", {})

    miniatura = (
        thumbs.get("maxres", {}).get("url")
        or thumbs.get("standard", {}).get("url")
        or thumbs.get("high", {}).get("url")
        or thumbs.get("medium", {}).get("url")
        or thumbs.get("default", {}).get("url")
        or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    )

    return {
        "titulo": snippet.get("title", ""),
        "videoId": video_id,
        "url": f"https://www.youtube.com/shorts/{video_id}",
        "miniatura": miniatura,
        "fecha_playlist": snippet.get("publishedAt", ""),
        "fecha_video": content.get("videoPublishedAt", "")
    }


# =========================================================
# VIDEOS / LIVES RECIENTES DEL CANAL
# Excluye Shorts para no duplicarlos con la sección superior.
# Shorts de YouTube pueden durar hasta 3 minutos, por eso
# se consideran "video largo" los contenidos > 180 segundos.
# Los directos activos siempre se permiten.
# =========================================================

def duracion_a_segundos(duracion):
    if not duracion:
        return 0

    patron = re.fullmatch(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
        duracion
    )

    if not patron:
        return 0

    horas = int(patron.group(1) or 0)
    minutos = int(patron.group(2) or 0)
    segundos = int(patron.group(3) or 0)

    return horas * 3600 + minutos * 60 + segundos


def obtener_playlist_uploads():
    for handle in (CHANNEL_HANDLE, f"@{CHANNEL_HANDLE}"):
        data = api_get(
            "channels",
            {
                "part": "contentDetails",
                "forHandle": handle,
                "maxResults": 1
            }
        )

        items = data.get("items", [])

        if items:
            return (
                items[0]["contentDetails"]
                ["relatedPlaylists"]["uploads"]
            )

    raise RuntimeError(
        f"No se encontró el canal con el handle {CHANNEL_HANDLE}"
    )


def obtener_ids_uploads(playlist_id, max_paginas=4):
    ids = []
    page_token = None

    for _ in range(max_paginas):
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50
        }

        if page_token:
            params["pageToken"] = page_token

        data = api_get("playlistItems", params)

        for item in data.get("items", []):
            video_id = item.get("contentDetails", {}).get("videoId")

            if video_id:
                ids.append(video_id)

        page_token = data.get("nextPageToken")

        if not page_token:
            break

    return ids


def obtener_detalles_videos(video_ids):
    detalles = []

    for inicio in range(0, len(video_ids), 50):
        lote = video_ids[inicio:inicio + 50]

        data = api_get(
            "videos",
            {
                "part": "snippet,contentDetails,liveStreamingDetails,status",
                "id": ",".join(lote),
                "maxResults": 50
            }
        )

        detalles.extend(data.get("items", []))

    return detalles


def convertir_video_destacado(item):
    video_id = item["id"]
    snippet = item.get("snippet", {})
    thumbs = snippet.get("thumbnails", {})

    miniatura = (
        thumbs.get("maxres", {}).get("url")
        or thumbs.get("standard", {}).get("url")
        or thumbs.get("high", {}).get("url")
        or thumbs.get("medium", {}).get("url")
        or thumbs.get("default", {}).get("url")
        or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    )

    estado_live = snippet.get("liveBroadcastContent", "none")

    return {
        "titulo": snippet.get("title", ""),
        "videoId": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "embed": f"https://www.youtube.com/embed/{video_id}?rel=0",
        "miniatura": miniatura,
        "fecha_video": snippet.get("publishedAt", ""),
        "en_vivo": estado_live == "live"
    }


def obtener_destacados_canal():
    uploads_playlist = obtener_playlist_uploads()
    ids = obtener_ids_uploads(uploads_playlist, max_paginas=4)
    videos = obtener_detalles_videos(ids)

    en_vivo = []
    videos_largos = []

    for item in videos:
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})
        status = item.get("status", {})

        if status.get("privacyStatus") != "public":
            continue

        estado_live = snippet.get("liveBroadcastContent", "none")

        # No mostramos directos programados que aún no empiezan.
        if estado_live == "upcoming":
            continue

        if estado_live == "live":
            en_vivo.append(item)
            continue

        segundos = duracion_a_segundos(content.get("duration", ""))

        # Evita que los Shorts vuelvan a aparecer aquí.
        if segundos > 180:
            videos_largos.append(item)

    clave_fecha = lambda item: item.get("snippet", {}).get("publishedAt", "")

    en_vivo.sort(key=clave_fecha, reverse=True)
    videos_largos.sort(key=clave_fecha, reverse=True)

    seleccion = (en_vivo + videos_largos)[:2]

    return [convertir_video_destacado(v) for v in seleccion]


# =========================================================
# GENERAR JSON
# =========================================================

resultado = {}

for segmento, playlist_id in PLAYLISTS.items():
    try:
        resultado[segmento] = ultimo_video_playlist(playlist_id)

        if resultado[segmento]:
            print(
                f"{segmento}: OK -> "
                f"{resultado[segmento]['titulo']}"
            )
        else:
            print(f"{segmento}: SIN VIDEOS")

    except Exception as e:
        print(f"{segmento}: ERROR -> {e}")

        resultado[segmento] = {
            "error": str(e),
            "playlistId": playlist_id
        }


try:
    resultado["youtube_destacados"] = obtener_destacados_canal()

    print(
        "youtube_destacados: "
        f"{len(resultado['youtube_destacados'])} encontrados"
    )

    for video in resultado["youtube_destacados"]:
        estado = "EN VIVO" if video["en_vivo"] else "VIDEO"
        print(f"  {estado}: {video['titulo']}")

except Exception as e:
    print(f"youtube_destacados: ERROR -> {e}")

    resultado["youtube_destacados"] = {
        "error": str(e)
    }


resultado["_actualizado"] = datetime.now(
    timezone.utc
).isoformat(timespec="seconds")


with open("data/segmentos.json", "w", encoding="utf-8") as f:
    json.dump(
        resultado,
        f,
        ensure_ascii=False,
        indent=2
    )


print("data/segmentos.json actualizado.")
