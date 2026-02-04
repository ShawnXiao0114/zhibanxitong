#!/bin/bash
echo "Starting server on internal port 8080 and external port 5638..."
echo "--------------------"
echo "Starting internal server on port 8080..."
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8080 &
INTERNAL_PID=$!
echo "Internal server started with PID: $INTERNAL_PID"
echo "Starting external server on port 5638..."
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 5638 &
EXTERNAL_PID=$!
echo "External server started with PID: $EXTERNAL_PID"
echo "--------------------"
echo "Servers started. Press any key to stop all servers."
read -p "" -n1 -s
echo "Stopping servers..."
kill $INTERNAL_PID 2>/dev/null
kill $EXTERNAL_PID 2>/dev/null
echo "Servers stopped."
