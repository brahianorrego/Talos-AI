# Pone Unreal a la izquierda y la estacion (Edge) a la derecha de la misma pantalla. Lo lanza VIVO_UNREAL.bat; corre unos minutos y termina.
# Uso: powershell -File acomodar_ventanas.ps1 -Porcentaje 60
param([int]$Porcentaje = 50, [int]$Segundos = 400)
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System; using System.Runtime.InteropServices;
public class V { [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int h2, bool r);
                 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
                 [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int w, int h2, uint f); }
"@
$a = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$uw = [int]($a.Width * $Porcentaje / 100); $ew = $a.Width - $uw
$hechas = @{}
$fin = (Get-Date).AddSeconds($Segundos)
while ((Get-Date) -lt $fin) {
    $u = Get-Process UnrealEditor -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    $e = Get-Process msedge -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like '*Estaci*' } | Select-Object -First 1
    if ($u) { [V]::ShowWindow($u.MainWindowHandle, 9) | Out-Null; [V]::MoveWindow($u.MainWindowHandle, $a.Left, $a.Top, $uw, $a.Height, $true) | Out-Null; $hechas['u'] = 1 }
    if ($e) { [V]::MoveWindow($e.MainWindowHandle, $a.Left + $uw, $a.Top, $ew, $a.Height, $true) | Out-Null; $hechas['e'] = 1 }
    if ($hechas.Count -eq 2) { Start-Sleep 20; $hechas = @{} } else { Start-Sleep 3 }                  # se repite por si el editor se vuelve a maximizar al terminar de cargar
}
