@echo off
rem Guarda tus cambios y los sincroniza con GitHub (asi tambien los ve el recordatorio diario).
title Guardar y sincronizar - Socio 3D
cd /d "%~dp0"
echo.
echo  Guardando y sincronizando tu negocio con GitHub...
echo.

git add -A
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Actualizacion %date% %time%"
) else (
    echo  No hay cambios nuevos para guardar.
)

git pull --rebase --autostash
if errorlevel 1 goto problema

git push
if errorlevel 1 goto problema

echo.
echo  Listo: todo guardado y sincronizado.
echo.
pause
exit /b 0

:problema
echo.
echo  Algo no salio bien. Saca una captura de esta ventana y mandasela a Claude.
echo.
pause
exit /b 1
