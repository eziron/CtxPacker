# CtxPacker (Context Packer)

Herramienta de línea de comandos diseñada para "condensar" la estructura y el código de un proyecto de programación en un único archivo Markdown (`.md`). 

Especialmente útil para generar **contexto limpio y estructurado para alimentar a LLMs** (como ChatGPT, Claude, o Llama) al hacer consultas sobre tu código base.

## 🚀 Características

*   **Exclusivo por defecto:** Ignora automáticamente carpetas ocultas (`.git`, `.vscode`, `.env`) para evitar ruido innecesario.
*   **Soporte `.gitignore`:** Interpreta tu gitignore nativo para omitir archivos irrelevantes.
*   **Perfiles Integrados (Presets):** Configuraciones predefinidas para `python`, `web`, `arduino` y `stm32` que filtran automáticamente basura (`__pycache__`, `node_modules`, binarios, etc.).
*   **Árbol de Directorios:** Genera una representación visual de la arquitectura de tu proyecto al inicio del documento.
*   **Modo "Solo Cabeceras":** Ideal para C/C++, permite extraer solo los archivos de interfaz (`.h`, `.hpp`) de ciertas carpetas para reducir el tamaño del prompt.

## 📋 Requisitos

*   **Python 3.6** o superior.
*   Librería externa `pathspec` (el instalador intentará instalarla por ti).

## 🛠 Instalación

Para poder usar el comando `ctxpack` desde cualquier terminal, descarga o clona este repositorio y ejecuta el instalador correspondiente a tu sistema operativo.

### Windows
1. Haz doble clic en el archivo `install.bat`.
2. Cierra la terminal actual y abre una nueva.

### Linux / Mac
1. Abre una terminal en la carpeta del repositorio.
2. Ejecuta:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

---

## 💻 Uso

El formato básico del comando es:

```bash
ctxpack <ruta_del_proyecto> <archivo_salida.md>
```

### Ejemplo Básico
Para condensar el proyecto en la carpeta actual y guardarlo en `contexto.md`:
```bash
ctxpack . contexto.md
```

### Ejemplo Avanzado (Recomendado)
Analizar un proyecto de Python, generar el árbol visual, incluir metadatos (líneas/tamaño) y respetar el `.gitignore`:

```bash
ctxpack ./mi_backend backend_resumen.md -p python -t -m -g
```

### Opciones y Filtros Principales

*   `-p, --profile <nombre>`: Aplica un filtro predefinido (`python`, `web`, `arduino`, `stm32`).
*   `-t, --add-tree`: Dibuja el árbol de carpetas al inicio del Markdown.
*   `-g, --use-gitignore`: Aplica las reglas de exclusión del `.gitignore` del proyecto.
*   `-m, --include-metadata`: Añade el peso y número de líneas arriba de cada bloque de código.
*   `-H, --add-hidden`: Fuerza la inclusión de archivos y carpetas ocultas (que empiezan por `.`).
*   `-xd, --exclude-dirs <dir1> <dir2>`: Excluye carpetas manualmente.
*   `-xf, --exclude-files <file1>`: Excluye archivos específicos.
*   `-xe, --exclude-extensions <ext1>`: Excluye extensiones (ej. `-xe .csv .json`).

Para ver todas las opciones disponibles, ejecuta: `ctxpack --help`