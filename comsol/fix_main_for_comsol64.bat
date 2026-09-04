@echo off
REM Fix main() in BAK_*.java so COMSOL File>Open does not call System.exit
cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$files = @('BAK_IO.java','BAK_OI.java','BAK_OI_fair.java');" ^
  "foreach ($f in $files) {" ^
  "  if (-not (Test-Path $f)) { Write-Host \"MISSING $f\"; continue }" ^
  "  $t = Get-Content -Raw -Path $f;" ^
  "  $t = $t -replace '(?s)public static void main\(String\[\] args\)\s*\{.*?\n  \}', \"public static void main(String[] args) {`r`n    run();`r`n  }\";" ^
  "  $t = $t -replace '(?m)^import java\.io\.IOException;\r?\n', '';" ^
  "  Set-Content -Path $f -Value $t -NoNewline;" ^
  "  Write-Host \"FIXED $f\";" ^
  "}"

echo.
echo Now compile (one at a time if needed):
echo   "C:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64\comsolcompile.exe" BAK_IO.java
pause
