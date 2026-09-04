@echo off
REM Compile BAK Model Java files for COMSOL 6.4 (Windows).
REM Run this on the university PC in the folder that contains BAK_IO.java.
REM Double-click this file, or run from cmd:  compile_models.bat

setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo === Looking for comsolcompile.exe ===
set "CC="

if exist "%COMSOL64%\Multiphysics\bin\win64\comsolcompile.exe" set "CC=%COMSOL64%\Multiphysics\bin\win64\comsolcompile.exe"
if not defined CC if exist "C:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64\comsolcompile.exe" set "CC=C:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64\comsolcompile.exe"
if not defined CC if exist "C:\Program Files\COMSOL\COMSOL63\Multiphysics\bin\win64\comsolcompile.exe" set "CC=C:\Program Files\COMSOL\COMSOL63\Multiphysics\bin\win64\comsolcompile.exe"
if not defined CC if exist "C:\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolcompile.exe" set "CC=C:\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolcompile.exe"

where comsolcompile >nul 2>&1
if not errorlevel 1 if not defined CC set "CC=comsolcompile"

if not defined CC (
  echo ERROR: comsolcompile.exe not found.
  echo Open COMSOL, check Help - About for the install path, then edit this bat
  echo and set CC= to ...\Multiphysics\bin\win64\comsolcompile.exe
  pause
  exit /b 1
)

echo Using: %CC%
echo.

for %%F in (BAK_IO.java BAK_OI.java BAK_OI_fair.java) do (
  if exist "%%F" (
    echo Compiling %%F ...
    "%CC%" "%%F"
    if errorlevel 1 (
      echo FAILED: %%F
      pause
      exit /b 1
    )
    echo OK: %%~nF.class
    echo.
  ) else (
    echo SKIP missing %%F
  )
)

echo.
echo === DONE ===
echo In COMSOL 6.4:
echo   File - Open
echo   File type: Compiled Model File for Java ^(*.class^)
echo   Open BAK_IO.class   ^(start with IO^)
echo   Then File - Save As - BAK_IO.mph
echo.
dir /b *.class 2>nul
pause
