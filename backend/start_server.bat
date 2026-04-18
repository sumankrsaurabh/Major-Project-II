@echo off
REM Start backend server without hot-reload (more stable on Windows)
REM This avoids multiprocessing issues with uvicorn's reload feature on Windows

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Chat with PDF - Backend Server (v2.0)                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo Starting server (stable mode without hot-reload)...
echo Press CTRL+C to stop.
echo.

uvicorn main:app --host 127.0.0.1 --port 8000

echo.
echo Server stopped.
pause
