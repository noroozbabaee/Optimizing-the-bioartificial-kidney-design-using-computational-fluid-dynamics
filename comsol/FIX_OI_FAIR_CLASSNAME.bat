@echo off
cd /d C:\Users\P70091319\Desktop\BAK
powershell -NoProfile -Command "(Get-Content -Raw BAK_OI_fair.java) -replace 'public class BAK_OI \{','public class BAK_OI_fair {' | Set-Content -NoNewline BAK_OI_fair.java"
echo.
findstr /n "public class BAK" BAK_OI_fair.java
echo.
echo If you see: public class BAK_OI_fair {
echo then compile with the next commands.
pause
