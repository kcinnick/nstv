@echo off
REM ============================================================================
REM Automation Script for NSTV Download Processing
REM ============================================================================
REM 
REM This script automatically processes completed downloads.
REM 
REM USAGE:
REM   1. Manual execution: Double-click this file or run from command prompt
REM   2. Windows Task Scheduler: Schedule to run every 15-30 minutes
REM
REM To set up Windows Task Scheduler:
REM   1. Open Task Scheduler
REM   2. Create Basic Task
REM   3. Name: "NSTV Download Processor"
REM   4. Trigger: Daily
REM   5. Repeat: Every 15 minutes
REM   6. Action: Start a program
REM   7. Program: Full path to this file
REM   8. Start in: C:\Users\Nick\nstv
REM
REM ============================================================================

echo ============================================================================
echo NSTV Download Processor
echo Start time: %date% %time%
echo ============================================================================
echo.

REM Navigate to project directory
cd /d C:\Users\Nick\nstv

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Run the download processor
echo Processing downloads...
python manage.py process_downloads --verbose

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

echo.
echo ============================================================================
if %EXIT_CODE% EQU 0 (
    echo [SUCCESS] Processing completed successfully
) else (
    echo [ERROR] Processing failed with exit code %EXIT_CODE%
)
echo End time: %date% %time%
echo ============================================================================

REM Keep window open only if run manually (not from Task Scheduler)
if "%1" neq "silent" (
    echo.
    echo Press any key to close...
    pause >nul
)

exit /b %EXIT_CODE%
