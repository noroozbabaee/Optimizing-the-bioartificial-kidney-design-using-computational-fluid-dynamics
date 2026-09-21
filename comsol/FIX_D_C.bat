@echo off
cd /d "%~dp0"
powershell -NoProfile -Command "Get-ChildItem BAK_*.java | ForEach-Object { $t=Get-Content -Raw $_.FullName; $t=[regex]::Replace($t,'(?m)^.*setIndex\(\"D_c\".*\r?\n',''); $t=[regex]::Replace($t,'(?m)^.*minput_velocity_src.*\r?\n',''); [IO.File]::WriteAllText($_.FullName,$t); Write-Host FIXED $_.Name }"
echo.
echo Recompile BAK_IO.java then File-Open BAK_IO.class
pause
