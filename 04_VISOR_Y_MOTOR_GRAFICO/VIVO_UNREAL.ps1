# UNA SOLA PANTALLA: Unreal en vivo a la izquierda (50 %) y la estación de tierra a la derecha (Vista del dron o Enseñar). Sin ventanas de consola.
# Lo lanza VIVO_UNREAL.bat. Abre en segundo plano la simulación en vivo (8767), el puente a Unreal (UDP 8770), la estación (8768), un vigilante que cierra
# el Crash Reporter, la estación en una ventana de Edge, el acomodador de ventanas y el editor de Unreal con vivo_unreal.py.
# Variables opcionales (antes de lanzar): DRONIA_VISTA=dron|mapa (por defecto dron), DRONIA_PANTALLA_UNREAL=60 (porcentaje de pantalla para Unreal).
$raiz = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$py = Join-Path $raiz '03_SIMULACION_RL\.venv\Scripts\pythonw.exe'
$aqui = $PSScriptRoot
$vista = if ($env:DRONIA_VISTA -eq 'mapa') { 'mapa' } else { 'dron' }          # dron = cámara del dron; mapa = mapa táctico (enseñar por puntos)
$pct = if ($null -ne $env:DRONIA_PANTALLA_UNREAL -and $env:DRONIA_PANTALLA_UNREAL -ne '') { [int]$env:DRONIA_PANTALLA_UNREAL } else { 0 }       # 0 = UNA SOLA VENTANA (la estación); Unreal corre minimizado y la estación muestra lo que ven sus cámaras. 50 = Unreal a la izquierda y la estación a la derecha (más lento: el editor dibuja su propia ventana)

# si quedaron copias de una corrida anterior se cierran (dos en_vivo.py se pisan el puerto y el puente se queda sin datos)
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'en_vivo\.py|puente_unreal\.py|estacion\servidor\.py|acomodar_ventanas' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep 1
Start-Process -FilePath $py -ArgumentList ('"' + (Join-Path $aqui 'en_vivo.py') + '"') -WindowStyle Hidden
for ($i = 0; $i -lt 60; $i++) { if (Get-NetTCPConnection -LocalPort 8767 -State Listen -ErrorAction SilentlyContinue) { break }; Start-Sleep 1 }       # el puente espera a que la simulación esté escuchando
Start-Process -FilePath $py -ArgumentList ('"' + (Join-Path $aqui 'puente_unreal.py') + '"') -WindowStyle Hidden
Start-Process -FilePath $py -ArgumentList ('"' + (Join-Path $aqui 'estacion\servidor.py') + '"') -WindowStyle Hidden
Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile', '-Command', 'while($true){Stop-Process -Name CrashReportClient -Force -ErrorAction SilentlyContinue; Start-Sleep 2}'

Add-Type -AssemblyName System.Windows.Forms
$a = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$uw = [int]($a.Width * $pct / 100); $ew = $a.Width - $uw
Start-Sleep 3
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$url = "http://127.0.0.1:8768/operacion.html?vista=$vista"
$depurar = @(); if ($env:DRONIA_DEPURAR) { $depurar = "--remote-debugging-port=9222", "--user-data-dir=$(Join-Path $aqui 'unreal\_cache\edge_depurar')" }      # solo para sacar fotos con capturar_estacion_cdp.mjs
if (Test-Path $edge) { Start-Process $edge -ArgumentList ($depurar + "--app=$url", "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding", "--disable-background-timer-throttling", "--window-position=$($a.Left + $uw),$($a.Top)", "--window-size=$ew,$($a.Height)") } else { Start-Process $url }
if ($pct -gt 0) { Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile', '-File', (Join-Path $aqui 'acomodar_ventanas.ps1'), '-Porcentaje', $pct }

$env:DRONIA_ORDEN = ((Join-Path $aqui 'unreal\vivo_unreal.py') -replace '\\', '/')
$ue = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$proy = Join-Path $env:USERPROFILE 'Documents\Unreal Projects\DronIA_Cancha\DronIA_Cancha.uproject'
if ($pct -gt 0) { Start-Process $ue -ArgumentList ('"' + $proy + '"'), '-nosplash', '-windowed', '-unattended', '-NoVSync', "-ResX=$uw", "-ResY=$($a.Height)", '-WinX=0', '-WinY=0' }
else { Start-Process $ue -WindowStyle Minimized -ArgumentList ('"' + $proy + '"'), '-nosplash', '-windowed', '-unattended', '-NoVSync', '-ResX=960', '-ResY=540' }       # una sola ventana: el editor arranca minimizado (con la ventana visible el juego baja de ~50 a ~30 cuadros por segundo)
