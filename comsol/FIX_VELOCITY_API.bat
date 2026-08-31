@echo off
cd /d "%~dp0"
powershell -NoProfile -Command "Get-ChildItem BAK_*.java | ForEach-Object { $t = Get-Content -Raw $_.FullName; $t = $t -replace '(?m)^.*minput_velocity_src.*\r?\n',''; [IO.File]::WriteAllText($_.FullName, $t); Write-Host STRIPPED $_.Name }"
echo Remove done. Recompile BAK_IO.java then open BAK_IO.class
pause
