@echo off
echo === Добавление пользователя в систему Reclamacia ===
set /p username=Введите логин:
python backend\cli_add_user.py %username%
pause
