@echo off
setlocal

set "SCRIPT_NAME=ctxpacker.py"
set "CMD_NAME=ctxpack"

:: 1. Verificar que existe el archivo Python
if not exist "%~dp0%SCRIPT_NAME%" (
    echo [ERROR] No se encuentra %SCRIPT_NAME% en esta carpeta.
    pause
    exit /b
)

echo Instalando dependencias...
pip install pathspec

echo.
echo Instalando %CMD_NAME% para Windows...

:: 2. Crear el archivo wrapper .bat
:: Este archivo es el que se ejecutará cuando escribas el comando
echo @echo off > "%~dp0%CMD_NAME%.bat"
echo python "%%~dp0%SCRIPT_NAME%" %%* >> "%~dp0%CMD_NAME%.bat"

echo  - Wrapper creado: %CMD_NAME%.bat

:: 3. Agregar la carpeta actual al PATH de Usuario usando PowerShell
echo  - Agregando carpeta actual al PATH de usuario...

set "CURRENT_DIR=%~dp0"
:: Quitamos la barra invertida final si existe
if "%CURRENT_DIR:~-1%"=="\" set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

powershell -Command ^
    "$path = [Environment]::GetEnvironmentVariable('Path', 'User'); " ^
    "$folder = '%CURRENT_DIR%'; " ^
    "if ($path -notlike * $folder *) { " ^
    "    [Environment]::SetEnvironmentVariable('Path', $path + ';' + $folder, 'User'); " ^
    "    Write-Host '   [OK] Ruta agregada al PATH.'; " ^
    "} else { " ^
    "    Write-Host '   [INFO] La ruta ya estaba en el PATH.'; " ^
    "}"

echo.
echo -------------------------------------------------------
echo  INSTALACION COMPLETADA
echo -------------------------------------------------------
echo  NOTA: Debes CERRAR esta terminal y abrir una nueva
echo  para que los cambios surtan efecto.
echo.
echo  Prueba escribiendo: %CMD_NAME% --help
echo -------------------------------------------------------
pause