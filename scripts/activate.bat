@echo off
chcp 65001 > nul

:: Переходим в корневую директорию
cd /d %~dp0\..

:: Запускаем setup.bat
call scripts\setup.bat

:: Запускаем dev режим из корня
echo 🚀 Запускаю dev режим...
uv run dev
