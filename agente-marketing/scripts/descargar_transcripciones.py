"""Descarga las transcripciones de los videos listados en conocimiento/charley-t/videos.csv.

Correlo en TU computadora (desde un servidor en la nube YouTube lo bloquea):

    pip install --upgrade youtube-transcript-api
    python scripts/descargar_transcripciones.py

Guarda un .txt por video en conocimiento/charley-t/transcripciones/ y saltea los que ya
existen, así que si se corta lo podés volver a correr.
"""

import csv
import sys
import time
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi

BASE = Path(__file__).resolve().parent.parent / "conocimiento" / "charley-t"
SALIDA = BASE / "transcripciones"
IDIOMAS = ["en", "en-US", "en-GB"]
PAUSA_SEGUNDOS = 10  # ir despacio: si se piden muchos seguidos, YouTube bloquea por unas horas
MAXIMO_ERRORES_SEGUIDOS = 3

# La consola de Windows a veces no puede mostrar ✓ / ✗.
sys.stdout.reconfigure(errors="replace")


def descargar_texto(video_id):
    # Versiones nuevas de la librería (1.x) usan una instancia; las viejas, un método de clase.
    if hasattr(YouTubeTranscriptApi, "fetch"):
        transcripcion = YouTubeTranscriptApi().fetch(video_id, languages=IDIOMAS)
        return " ".join(s.text for s in transcripcion.snippets)
    transcripcion = YouTubeTranscriptApi.get_transcript(video_id, languages=IDIOMAS)
    return " ".join(s["text"] for s in transcripcion)


def main():
    SALIDA.mkdir(exist_ok=True)
    with open(BASE / "videos.csv", encoding="utf-8") as f:
        videos = list(csv.DictReader(f))

    errores_seguidos = 0
    for video in videos:
        destino = SALIDA / f"{int(video['n']):03d}-{video['id']}.txt"
        if destino.exists():
            continue
        try:
            texto = descargar_texto(video["id"])
        except Exception as error:
            print(f"✗ {video['n']}. {video['titulo']}: {type(error).__name__}")
            errores_seguidos += 1
            if errores_seguidos >= MAXIMO_ERRORES_SEGUIDOS:
                print("\nFallaron varios seguidos, así que paro. Mandá este error completo:\n")
                print(f"{type(error).__name__}: {error}")
                return
            time.sleep(PAUSA_SEGUNDOS)
            continue
        errores_seguidos = 0
        destino.write_text(f"# {video['titulo']}\n{video['url']}\n\n{texto}\n", encoding="utf-8")
        print(f"✓ {video['n']}. {video['titulo']}")
        time.sleep(PAUSA_SEGUNDOS)


if __name__ == "__main__":
    main()
