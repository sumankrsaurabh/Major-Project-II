@echo off
REM Start backend server with hot-reload for development
REM Use this only for development - use start_server.bat for production

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Chat with PDF - Backend Server (Development Mode)        ║
echo ║  Hot-reload enabled - server will restart on code changes ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo Starting server with hot-reload...
echo Press CTRL+C to stop.
echo.

REM Use --reload with --workers 1 to avoid multiprocessing on Windows
uvicorn main:app --host 127.0.0.1 --port 8000 --reload --workers 1

echo.
echo Server stopped.
pause
