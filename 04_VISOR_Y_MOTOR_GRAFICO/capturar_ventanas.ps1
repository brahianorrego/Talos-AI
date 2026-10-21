# Foto de las ventanas de la estación (Edge) y de Unreal aunque otra ventana las tape (PrintWindow). Sirve para dejar evidencia de la «una sola pantalla».
# Uso: powershell -File capturar_ventanas.ps1 -Salida ruta_sin_extension     -> <salida>_estacion.png, <salida>_unreal.png y <salida>_juntas.png
param([string]$Salida = "$PSScriptRoot\mediciones\capturas\una_pantalla")
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class P { [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
                 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r); public struct R { public int L, T, Rr, B; } }
"@
function Foto($proc, $filtro, $archivo) {
    $p = Get-Process $proc -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -like $filtro } | Select-Object -First 1
    if (-not $p) { return $null }
    $r = New-Object P+R; [P]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
    $w = $r.Rr - $r.L; $h = $r.B - $r.T
    $bmp = New-Object System.Drawing.Bitmap $w, $h; $g = [System.Drawing.Graphics]::FromImage($bmp); $dc = $g.GetHdc()
    [P]::PrintWindow($p.MainWindowHandle, $dc, 2) | Out-Null; $g.ReleaseHdc($dc); $g.Dispose()
    $bmp.Save($archivo); return $bmp
}
$a = Foto 'msedge' '*Estaci*' "${Salida}_estacion.png"
$b = Foto 'UnrealEditor' '*Unreal*' "${Salida}_unreal.png"
if ($a -and $b) {
    $j = New-Object System.Drawing.Bitmap ($a.Width + $b.Width), ([Math]::Max($a.Height, $b.Height)); $g = [System.Drawing.Graphics]::FromImage($j)
    $g.DrawImage($b, 0, 0); $g.DrawImage($a, $b.Width, 0); $j.Save("${Salida}_juntas.png")
}
"estacion=$([bool]$a) unreal=$([bool]$b)"
