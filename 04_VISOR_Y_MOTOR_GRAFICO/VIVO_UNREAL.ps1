# UNA SOLA PANTALLA: Unreal en vivo a la izquierda (50 %) y la estación de tierra a la derecha (Vista del dron o Enseñar). Sin ventanas de consola.
# Lo lanza VIVO_UNREAL.bat. Abre en segundo plano la simulación en vivo (8767), el puente a Unreal (UDP 8770), la estación (8768), un vigilante que cierra
# el Crash Reporter, la estación en una ventana de Edge, el acomodador de ventanas y el editor de Unreal con vivo_unreal.py.
# Variables opcionales (antes de lanzar): DRONIA_VISTA=dron|ens|3d (por defecto ens), DRONIA_PANTALLA_UNREAL=60 (porcentaje de pantalla para Unreal).
$raiz = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$py = Join-Path $raiz '03_SIMULACION_RL\.venv\Scripts\pythonw.exe'
$aqui = $PSScriptRoot
$vista = if ($env:DRONIA_VISTA) { $env:DRONIA_VISTA } else { 'ens' }
$pct = if ($env:DRONIA_PANTALLA_UNREAL) { [int]$env:DRONIA_PANTALLA_UNREAL } else { 50 }

foreach ($s in 'en_vivo.py', 'puente_unreal.py', 'estacion\servidor.py') {
    Start-Process -FilePath $py -ArgumentList ('"' + (Join-Path $aqui $s) + '"') -WindowStyle Hidden
}
Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile', '-Command', 'while($true){Stop-Process -Name CrashReportClient -Force -ErrorAction SilentlyContinue; Start-Sleep 2}'

Add-Type -AssemblyName System.Windows.Forms
$a = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$uw = [int]($a.Width * $pct / 100); $ew = $a.Width - $uw
Start-Sleep 3
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$url = "http://127.0.0.1:8768/?modo=$vista"
$depurar = @(); if ($env:DRONIA_DEPURAR) { $depurar = "--remote-debugging-port=9222", "--user-data-dir=$(Join-Path $aqui 'unreal\_cache\edge_depurar')" }      # solo para sacar fotos con capturar_estacion_cdp.mjs
if (Test-Path $edge) { Start-Process $edge -ArgumentList ($depurar + "--app=$url", "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding", "--disable-background-timer-throttling", "--window-position=$($a.Left + $uw),$($a.Top)", "--window-size=$ew,$($a.Height)") } else { Start-Process $url }
Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile', '-File', (Join-Path $aqui 'acomodar_ventanas.ps1'), '-Porcentaje', $pct

$env:DRONIA_ORDEN = ((Join-Path $aqui 'unreal\vivo_unreal.py') -replace '\\', '/')
$ue = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$proy = Join-Path $env:USERPROFILE 'Documents\Unreal Projects\DronIA_Cancha\DronIA_Cancha.uproject'
Start-Process $ue -ArgumentList ('"' + $proy + '"'), '-nosplash', '-windowed', '-unattended', '-NoVSync', "-ResX=$uw", "-ResY=$($a.Height)", '-WinX=0', '-WinY=0'
