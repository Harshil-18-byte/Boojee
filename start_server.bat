@echo off
cd /d "%~dp0"
start http://localhost:5000
:loop
echo Starting Boojee Cafe Backend Server...
.\venv\Scripts\python.exe app.py
echo Server crashed or exited. Restarting in 5 seconds...
timeout /t 5
goto loop
