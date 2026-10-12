@echo off
echo Запускаем проект "IMDb Explorer"...

REM Переходим в папку с проектом. Ключ /d нужен, чтобы сменить диск, если надо.
cd /d "C:\Users\UserNik\Documents\portfolio\imdb_top_1000_analysis (IMDb Explorer)"

REM Запускаем Streamlit
streamlit run main.py

echo.
echo Дашборд запущен. Это окно можно закрыть.