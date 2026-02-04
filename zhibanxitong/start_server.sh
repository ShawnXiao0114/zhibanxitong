#!/bin/bash
echo "Starting server..."
echo "--------------------"
python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8080
echo "--------------------"
echo "Server stopped."
read -p "Press any key to exit..." -n1 -s
