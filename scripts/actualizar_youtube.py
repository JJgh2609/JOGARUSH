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
