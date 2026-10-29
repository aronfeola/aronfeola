@echo off
REM Doble clic para descargar las transcripciones de los videos (Windows).
cd /d "%~dp0"
python -m pip install --upgrade youtube-transcript-api
echo.
python scripts\descargar_transcripciones.py
echo.
pause
