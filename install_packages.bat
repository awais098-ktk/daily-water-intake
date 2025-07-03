@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
pip install flask flask-sqlalchemy flask-login werkzeug pillow requests
python check_imports.py
pause
