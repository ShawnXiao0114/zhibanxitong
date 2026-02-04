@echo off
echo Starting server on internal port 8080 and external port 5638...
echo --------------------
echo Starting internal server on port 8080...
start "Internal Server" python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080
echo Starting external server on port 5638...
start "External Server" python -m uvicorn main:app --reload --host 0.0.0.0 --port 5638
echo --------------------
echo Servers started. Press any key to stop all servers.
pause
taskkill /F /FI "WINDOWTITLE eq Internal Server*" 2>nul
taskkill /F /FI "WINDOWTITLE eq External Server*" 2>nul
echo Servers stopped.
