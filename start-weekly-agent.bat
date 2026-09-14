@echo off
REM ============================================================
REM  Agent dinh ky: quet insight TikTok roi viet kich ban
REM ============================================================
REM  Chay tay (bam dup chuot):
REM    start-weekly-agent.bat              chay that, moi job dang bat
REM    start-weekly-agent.bat --dry-run    chi in lenh, KHONG ton tien
REM    start-weekly-agent.bat --job <ten>  chay 1 job
REM
REM  Windows Task Scheduler goi voi co --task o DAU tien:
REM    start-weekly-agent.bat --task       chay xong tu dong dong
REM ============================================================

setlocal
cd /d "%~dp0"

REM Bat UTF-8 de log tieng Viet khong bi vo
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

REM Tach co --task ra, KHONG truyen xuong python
set KHONG_CHO_BAM=0
if /i "%~1"=="--task" (
    set KHONG_CHO_BAM=1
    shift
)

REM Gom cac tham so con lai sau khi da bo --task
set THAM_SO=
:gom
if "%~1"=="" goto xong_gom
set THAM_SO=%THAM_SO% %1
shift
goto gom
:xong_gom

echo.
echo === Agent dinh ky: bat dau %date% %time% ===
echo.

python weekly_agent.py%THAM_SO%
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE%==0 (
    echo === XONG: moi viec tron ven ===
) else (
    echo === CO JOB HONG: xem output\_agent-logs\ de biet hong o dau ===
)

if %KHONG_CHO_BAM%==1 exit /b %EXITCODE%
pause
exit /b %EXITCODE%
