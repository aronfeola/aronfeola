"""Descarga las transcripciones de los videos listados en conocimiento/charley-t/videos.csv.

Correlo en TU computadora (desde un servidor en la nube YouTube lo bloquea):

    pip install youtube-transcript-api
    python scripts/descargar_transcripciones.py

Guarda un .txt por video en conocimiento/charley-t/transcripciones/ y saltea los que ya
existen, así que si se corta lo podés volver a correr.
"""

import csv
import time
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi

BASE = Path(__file__).resolve().parent.parent / "conocimiento" / "charley-t"
SALIDA = BASE / "transcripciones"
PAUSA_SEGUNDOS = 3


def main():
    SALIDA.mkdir(exist_ok=True)
    api = YouTubeTranscriptApi()
    with open(BASE / "videos.csv", encoding="utf-8") as f:
        videos = list(csv.DictReader(f))

    for video in videos:
        destino = SALIDA / f"{int(video['n']):03d}-{video['id']}.txt"
        if destino.exists():
            continue
        try:
            transcripcion = api.fetch(video["id"], languages=["en"])
        except Exception as error:
            print(f"✗ {video['n']}. {video['titulo']}: {type(error).__name__}")
            continue
        texto = " ".join(s.text for s in transcripcion.snippets)
        destino.write_text(f"# {video['titulo']}\n{video['url']}\n\n{texto}\n", encoding="utf-8")
        print(f"✓ {video['n']}. {video['titulo']}")
        time.sleep(PAUSA_SEGUNDOS)


if __name__ == "__main__":
    main()
