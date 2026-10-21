Start-Sleep 8
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'entrenar_master' } | ForEach-Object { (Get-Process -Id $_.ProcessId).PriorityClass = 'BelowNormal' }
