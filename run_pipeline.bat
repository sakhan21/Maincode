@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
cd /d %~dp0

echo === mainpipe: Windows one-click runner ===

IF EXIST "venv\Scripts\activate.bat" (
    echo Detected existing virtual environment: venv
    call "venv\Scripts\activate.bat"
) ELSE (
    echo No virtual environment detected. Using system Python.
)

echo Running pipeline with config: configs\local.yaml
python -m mainpipe.cli --config configs\local.yaml

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Pipeline exited with a non-zero status: %ERRORLEVEL%
) ELSE (
    echo.
    echo [OK] Pipeline finished successfully.
)

echo.
pause
ENDLOCAL
