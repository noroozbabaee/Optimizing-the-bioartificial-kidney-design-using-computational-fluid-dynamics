@echo off
REM One-shot COMSOL 6.4 sanitizer for BAK_*.java on the university remote PC.
REM Run from Desktop\BAK:  fix_for_comsol64.bat
REM Removes every API call known to throw Unknown parameter / Unknown feature ID.

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix_for_comsol64.ps1"
if errorlevel 1 exit /b 1
echo.
echo Next: delete *.class and comsolcompile the three BAK_*.java files.
pause
