@echo off
echo Starting server...
echo --------------------
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8080
echo --------------------
echo Server stopped.
pause
