@echo off
cd /d C:\dev\trade_accounting
call .venv\Scripts\activate
python manage.py runserver 127.0.0.1:8000


