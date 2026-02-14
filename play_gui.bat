@echo off
cd /d C:\Users\cella\Games\dnd_roguelike

REM Run GUI and keep window open if there is an error
py -3.11 main_gui.py
echo.
echo The game has exited. If there was an error, it should be shown above.
pause
