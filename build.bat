@echo off
REM ============================================================================
REM  🐋 WhaleTermux — Build Workflow
REM  Builds the .deb package and generates full APT repository metadata.
REM
REM  Usage:  build.bat              (clean build)
REM          build.bat --serve      (build + serve locally on port 8000)
REM          build.bat --help       (show help)
REM ============================================================================
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%"

:parse_args
if "%~1"=="--serve" set "SERVE=1" & shift & goto :parse_args
if "%~1"=="--help" goto :help
if "%~1"=="-h" goto :help
if "%~1"=="" goto :run

:help
echo.
echo  🐋 WhaleTermux Build Script
echo.
echo  Usage:
echo    build.bat              Build .deb + APT repo metadata
echo    build.bat --serve      Build then serve locally on port 8000
echo    build.bat --help       Show this help
echo.
exit /b 0

:run
echo.
echo ========================================
echo    🐋 WhaleTermux Build System
echo ========================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.
    exit /b 1
)

echo [1/2] Building .deb and APT repo...
cd /d "%PROJECT_DIR%"
python "%PROJECT_DIR%build_all.py"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build failed!
    exit /b 1
)

echo.
echo ========================================
echo    BUILD COMPLETE
echo ========================================
echo.
echo   Output:
echo     .deb:       %%PROJECT_DIR%%whale-agent_1.0.0_all.deb
echo     Packages:   %%PROJECT_DIR%%termux-repo\repo\dists\stable\main\binary-all\Packages
echo     Release:    %%PROJECT_DIR%%termux-repo\repo\dists\stable\Release
echo.

if "%SERVE%"=="1" (
    echo [2/2] Starting HTTP server on port 8000...
    echo   URL: http://localhost:8000
    cd /d "%PROJECT_DIR%termux-repo\repo"
    python -m http.server 8000
)

echo Done!
exit /b 0
