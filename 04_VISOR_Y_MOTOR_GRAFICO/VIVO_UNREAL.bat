@echo off
rem UNA SOLA PANTALLA: Unreal en vivo a la izquierda (60 %) y la estacion de tierra a la derecha. Todo corre sin ventanas de consola (ver VIVO_UNREAL.ps1).
rem Opcional antes de lanzar: set DRONIA_VISTA=mapa  (abre en el mapa táctico en vez de la cámara del dron)   set DRONIA_PANTALLA_UNREAL=70
start "" powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0VIVO_UNREAL.ps1"
