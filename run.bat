@echo off
echo ===================================================
echo   CLINICOM - Web Application Startup
echo ===================================================
echo.
echo Installing required packages (including Flask)...
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
    python -m pip install -r requirements.txt
)
echo.
echo Launching the beautiful CLINICOM web interface...
echo You can access it at: http://127.0.0.1:5000
echo.

:: Open the default web browser after a short delay
start "" http://127.0.0.1:5000

:: Run the Flask app
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe app.py
) else (
    python app.py
)
pause
