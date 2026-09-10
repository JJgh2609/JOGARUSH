import os
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_KEY = os.environ["YOUTUBE_API_KEY"]

PLAYLISTS = {
    "news": "PLfFb-ddywg-c",
    "tips": "PLUXoJshp-aP0",
    "futbol": "PLaPVD_LX9Q-w",
    "gaming": "PLSkijo2yWyuw",
    "cine_anime": "PLbo7JjRu4tCI"
}

def obtener_items(playlist_id):
    params = urllib.parse.urlencode({
        "part": "snippet,contentDetails",
        "playlistId": playlist_id,
        "maxResults": 50,
        "key": API_KEY
    })
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?{params}"
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)

def ultimo_video(playlist_id):
    data = obtener_items(playlist_id)
    items = data.get("items", [])
    if not items:
        return None

    item = max(items, key=lambda x: x.get("snippet", {}).get("publishedAt", ""))

    snippet = item.get("snippet", {})
    content = item.get("contentDetails", {})
    video_id = content.get("videoId") or snippet.get("resourceId", {}).get("videoId")
    if not video_id:
        return None

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

resultado = {}

for segmento, playlist_id in PLAYLISTS.items():
    try:
        resultado[segmento] = ultimo_video(playlist_id)
        print(f"{segmento}: OK")
    except Exception as e:
        print(f"{segmento}: ERROR -> {e}")
        resultado[segmento] = {
            "error": str(e),
            "playlistId": playlist_id
        }

resultado["_actualizado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

with open("data/segmentos.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print("data/segmentos.json actualizado.")
