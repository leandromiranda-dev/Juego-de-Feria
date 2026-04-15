@echo off
echo Iniciando Esquiva los Meteoritos...

REM Usar entorno virtual si existe, sino usar python del sistema
if exist "venv_juego\Scripts\python.exe" (
    venv_juego\Scripts\python.exe game.py
) else (
    echo AVISO: Entorno virtual no encontrado.
    echo Ejecuta primero: instalar.bat
    echo.
    echo Intentando con Python del sistema...
    python game.py
)
pause
