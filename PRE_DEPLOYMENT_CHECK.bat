@echo off
REM ========================================
REM Auto Dashboard - Pre-Deployment Checklist
REM ========================================
REM Run this before deploying to Render
REM ========================================

setlocal enabledelayedexpansion

echo.
echo ======================================
echo AUTO DASHBOARD - DEPLOYMENT CHECKLIST
echo ======================================
echo.

set passed=0
set failed=0

REM Color codes (Windows CMD supports limited colors)
REM 2 = Green, 4 = Red, 6 = Yellow, 9 = Light Blue

REM Function to check file existence
:CHECK_FILE
if exist "%~1" (
    echo [OK] %~2
    set /a passed+=1
) else (
    echo [FAIL] %~2 NOT FOUND: %~1
    set /a failed+=1
)
goto :eof

REM Check required files
echo [1/4] Checking required files...
call :CHECK_FILE "Procfile" "Procfile exists"
call :CHECK_FILE "render.yaml" "render.yaml exists"
call :CHECK_FILE "requirements.txt" "requirements.txt exists"
call :CHECK_FILE "runtime.txt" "runtime.txt exists"
call :CHECK_FILE "run.py" "run.py exists"
call :CHECK_FILE ".gitignore" ".gitignore exists"
call :CHECK_FILE "backend\app.py" "backend/app.py exists"
call :CHECK_FILE "backend\__init__.py" "backend/__init__.py exists"
call :CHECK_FILE "backend\pdf_parser.py" "backend/pdf_parser.py exists"

echo.
echo [2/4] Checking Git configuration...
if exist ".git" (
    echo [OK] Git repository initialized
    set /a passed+=1
) else (
    echo [FAIL] Git repository NOT initialized
    set /a failed+=1
    echo       Run: git init
)

echo.
echo [3/4] Checking Python environment...
if exist ".venv" (
    echo [OK] Virtual environment exists (.venv)
    set /a passed+=1
) else (
    echo [INFO] Virtual environment not found locally (OK for cloud)
)

echo.
echo [4/4] Checking environment files...
if exist ".env.local" (
    echo [INFO] .env.local exists (ensure it's in .gitignore)
    set /a passed+=1
) else (
    echo [INFO] .env.local not found (create with your secrets)
)

if exist ".env.production" (
    echo [INFO] .env.production exists (ensure it's in .gitignore)
    set /a passed+=1
)

echo.
echo ======================================
echo SUMMARY
echo ======================================
echo Checks Passed: %passed%
echo Checks Failed: %failed%
echo.

if %failed% equ 0 (
    echo [SUCCESS] All checks passed!
    echo.
    echo Next steps:
    echo 1. git add .
    echo 2. git commit -m "Deploy to Render"
    echo 3. git push origin main
    echo 4. Go to render.com and create Web Service
    echo 5. Connect GitHub repository
    echo 6. Configure environment variables
    echo 7. Click "Create Web Service"
    echo.
) else (
    echo [WARNING] Some checks failed. Fix issues before deploying.
)

echo.
echo Documentation files:
echo - DEPLOYMENT_READY.md (Complete overview)
echo - RENDER_DEPLOYMENT_GUIDE.md (Step-by-step guide)
echo - DEPLOYMENT_CHECKLIST.md (Detailed checklist)
echo - DEPLOYMENT_ARCHITECTURE.md (System architecture)
echo.

pause
