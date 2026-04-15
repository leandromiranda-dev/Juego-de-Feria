@echo off
echo ============================================
echo  INSTALADOR - Esquiva los Meteoritos
echo ============================================
echo.

REM Crear entorno virtual limpio
echo [1/4] Creando entorno virtual limpio...
python -m venv venv_juego
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual.
    echo Asegurate de tener Python 3.8-3.12 instalado.
    pause
    exit /b 1
)

echo [2/4] Activando entorno virtual...
call venv_juego\Scripts\activate.bat

echo [3/4] Instalando dependencias (sin TensorFlow)...
python -m pip install --upgrade pip --quiet
pip install opencv-python mediapipe==0.10.32 numpy --quiet
if errorlevel 1 (
    echo ERROR en la instalacion. Revisa tu conexion a internet.
    pause
    exit /b 1
)

echo [4/4] Instalacion completada!
echo.
echo ============================================
echo  Para JUGAR, ejecuta:  jugar.bat
echo ============================================
echo.
pause
