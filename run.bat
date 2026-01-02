@echo off
echo Cleaning cache...
if exist __pycache__ rmdir /s /q __pycache__
if exist gui.pyc del /f /q gui.pyc

echo Starting Gambito...
python gui.py
pause
