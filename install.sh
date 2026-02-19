#!/bin/bash

# Nombre del script de python y del comando deseado
SCRIPT_NAME="ctxpacker.py"
CMD_NAME="ctxpack"

# Obtener la ruta absoluta del directorio actual
CURRENT_DIR=$(pwd)
SCRIPT_PATH="$CURRENT_DIR/$SCRIPT_NAME"

# 1. Verificar si el archivo python existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: No se encuentra $SCRIPT_NAME en este directorio."
    exit 1
fi

echo "Instalando dependencias (pathspec)..."
python3 -m pip install pathspec --break-system-packages 2>/dev/null || python3 -m pip install pathspec

echo "Instalando comando global: $CMD_NAME..."

# 2. Asegurar que tenga la linea Shebang al inicio
if ! head -n 1 "$SCRIPT_PATH" | grep -q "python"; then
    echo "Agregando Shebang a $SCRIPT_NAME..."
    sed -i '1s/^/#!\/usr\/bin\/env python3\n/' "$SCRIPT_PATH"
fi

# 3. Dar permisos de ejecución
chmod +x "$SCRIPT_PATH"
echo "Permisos de ejecución concedidos."

# 4. Crear enlace simbólico en /usr/local/bin (requiere sudo)
echo "Creando enlace simbólico en /usr/local/bin (se requerirá contraseña de sudo)..."
if [ -L "/usr/local/bin/$CMD_NAME" ]; then
    sudo rm "/usr/local/bin/$CMD_NAME"
fi

sudo ln -s "$SCRIPT_PATH" "/usr/local/bin/$CMD_NAME"

echo "-----------------------------------"
echo "¡Instalación completada con éxito!"
echo "Ahora puedes ejecutar: $CMD_NAME ./mi_proyecto salida.md"
echo "Para ver la ayuda escribe: $CMD_NAME --help"
echo "-----------------------------------"