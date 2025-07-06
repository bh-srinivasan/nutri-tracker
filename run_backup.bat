@echo off
REM Automated Database Backup Script for Nutri Tracker
REM Run this daily via Windows Task Scheduler

echo ========================================
echo Nutri Tracker Database Backup
echo ========================================
echo Started at: %date% %time%

REM Change to the application directory
cd /d "c:\Users\bhsrinivasan\Downloads\Learning\Vibe Coding\Nutri_Tracker"

REM Activate virtual environment and run backup
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python backup_database.py full
    echo.
    echo ========================================
    echo Backup completed at: %date% %time%
    echo ========================================
) else (
    echo ERROR: Virtual environment not found!
    echo Please ensure .venv directory exists
)

REM Keep window open for 5 seconds to see results
timeout /t 5 /nobreak > nul
