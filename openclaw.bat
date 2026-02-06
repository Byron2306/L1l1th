@echo off
cd /d "C:\LuciferOS_FULL"
call .venv\Scripts\activate.bat
python openclaw\lilith_bridge.py %*
