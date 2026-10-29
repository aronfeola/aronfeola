@echo off
title Instalar Socio de negocios 3D
echo.
echo  Instalador del Socio de negocios 3D
echo  ------------------------------------
echo  Tarda unos minutos. No cierres esta ventana hasta que diga LISTO.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1"
echo.
echo  Ya podes cerrar esta ventana.
pause
