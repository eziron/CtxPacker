#!/usr/bin/env python3
import os
import argparse
import time
from typing import List, Set, Optional

try:
    import pathspec
except ImportError:
    print("Error: La librería 'pathspec' no está instalada.")
    print("Por favor, instálala con: pip install pathspec")
    exit(1)

# --- CONFIGURACIÓN Y CONSTANTES ---

LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "jsx",
    ".tsx": "tsx",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".json": "json",
    ".md": "markdown",
    ".astro": "astro",
    ".sql": "sql",
    ".sh": "shell",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".xml": "xml",
    ".java": "java",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".rs": "rust",
    ".go": "go",
    ".rb": "ruby",
    ".ino": "cpp",
    ".d.ts": "typescript",
}

# Configuración por defecto (si no se usa perfil)
DEFAULT_EXCLUDE_DIRS = {"node_modules", ".git", "dist", "build", "venv", ".venv", "__pycache__", ".astro"}
DEFAULT_EXCLUDE_FILES = {"package-lock.json", ".DS_Store"}
DEFAULT_EXCLUDE_EXTS = {".svg", ".ico", ".lock", ".log"}

# Definición de Perfiles (Presets)
PRESETS = {
    "stm32": {
        "exclude_dirs": DEFAULT_EXCLUDE_DIRS | {"public", ".vscode", ".github", "Drivers", "Middlewares", "USB_DEVICE", "USB_Device", "build"},
        "exclude_files": DEFAULT_EXCLUDE_FILES | {"LICENSE", "Makefile", "README.md", "library.properties", ".mxproject", ".gitignore", ".stm32env"},
        "exclude_extensions": DEFAULT_EXCLUDE_EXTS | {".cfg", ".s", ".ioc", ".lockb", ".md", ".ld", ".yaml", ".make"},
        "max_file_size": "250K",
    },
    "arduino": {
        "exclude_dirs": DEFAULT_EXCLUDE_DIRS | {"public", ".vscode", ".github"},
        "exclude_files": DEFAULT_EXCLUDE_FILES | {"bun.lock", "LICENSE", "Makefile", "README.md", "library.properties"},
        "exclude_extensions": DEFAULT_EXCLUDE_EXTS | {".lockb", ".md"},
        "max_file_size": "250K",
    },
    "web": {"exclude_dirs": DEFAULT_EXCLUDE_DIRS | {"public", ".vscode", ".github"}, "exclude_files": DEFAULT_EXCLUDE_FILES | {"bun.lock"}, "exclude_extensions": DEFAULT_EXCLUDE_EXTS | {".lockb"}, "max_file_size": "250K"},
    "python": {
        "exclude_dirs": DEFAULT_EXCLUDE_DIRS | {"env", ".pytest_cache", ".mypy_cache", ".ipynb_checkpoints", ".tox", "htmlcov", ".idea"},
        "exclude_files": DEFAULT_EXCLUDE_FILES | {"poetry.lock", "Pipfile.lock", ".coverage"},
        "exclude_extensions": DEFAULT_EXCLUDE_EXTS | {".pyc", ".pyo", ".pyd", ".whl", ".pkl", ".so"},
        "max_file_size": "250K",
    },
}

# Extensiones por defecto para modo "Solo Cabeceras"
DEFAULT_HEADER_EXTS = {".h", ".hpp", ".hh", ".cuh", ".d.ts", ".pyi", ".java-interface"}


# --- FUNCIONES AUXILIARES ---


def parse_size(size_str: str) -> int:
    """Convierte un string de tamaño (ej. '100K', '2M') a bytes."""
    if not size_str:
        return None
    size_str = size_str.upper()
    if size_str.endswith("K"):
        return int(float(size_str[:-1]) * 1024)
    if size_str.endswith("M"):
        return int(float(size_str[:-1]) * 1024 * 1024)
    if size_str.endswith("G"):
        return int(float(size_str[:-1]) * 1024 * 1024 * 1024)
    return int(size_str)


def format_bytes(byte_count: int) -> str:
    """Formatea bytes a KB/MB."""
    if byte_count is None:
        return "N/A"
    if byte_count > 1024 * 1024:
        return f"{byte_count / (1024 * 1024):.2f} MB"
    if byte_count > 1024:
        return f"{byte_count / 1024:.2f} KB"
    return f"{byte_count} Bytes"


def is_text_file(filepath: str) -> bool:
    """Detecta archivos binarios buscando bytes nulos."""
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return False
    except Exception:
        return False
    return True


def is_header_file(filename: str, header_extensions: Set[str]) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in header_extensions


def is_in_header_path(file_rel_path: str, header_paths: Set[str]) -> bool:
    """Verifica si la ruta relativa del archivo comienza con alguna ruta de 'solo headers'."""
    file_rel_path = file_rel_path.replace(os.sep, "/")
    for path in header_paths:
        path = path.replace(os.sep, "/")
        if file_rel_path.startswith(path + "/") or file_rel_path == path:
            return True
    return False


# --- GENERACIÓN DEL ÁRBOL ---


def generate_tree(start_path: str, project_root: str, exclude_dirs: Set[str], spec: Optional[pathspec.PathSpec], add_hidden: bool, prefix: str = "") -> List[str]:
    tree_lines = []
    try:
        entries = sorted(os.scandir(start_path), key=lambda e: e.name)
    except OSError:
        return []

    # Filtrado inicial para el árbol (Ocultos excluidos por defecto)
    filtered_entries = []
    for e in entries:
        if not add_hidden and e.name.startswith("."):
            continue
        filtered_entries.append(e)

    dir_entries = [e for e in filtered_entries if e.is_dir()]
    file_entries = [e for e in filtered_entries if e.is_file()]
    sorted_entries = dir_entries + file_entries

    for i, entry in enumerate(sorted_entries):
        connector = "└── " if i == len(sorted_entries) - 1 else "├── "
        tree_lines.append(f"{prefix}{connector}{entry.name}")

        if entry.is_dir():
            relative_path = os.path.relpath(entry.path, project_root).replace(os.sep, "/")
            is_excluded_by_cmd = entry.name in exclude_dirs
            is_excluded_by_gitignore = spec and spec.match_file(relative_path)

            if is_excluded_by_cmd or is_excluded_by_gitignore:
                tree_lines.append(f"{prefix}│   └── [...]")
            else:
                extension = "    " if i == len(sorted_entries) - 1 else "│   "
                tree_lines.extend(generate_tree(entry.path, project_root, exclude_dirs, spec, add_hidden, prefix + extension))
    return tree_lines


# --- FUNCIÓN PRINCIPAL ---


def generate_project_summary(
    project_path: str,
    output_file: str,
    exclude_dirs: Set[str],
    exclude_files: Set[str],
    exclude_extensions: Set[str],
    use_gitignore: bool,
    gitignore_path: Optional[str],
    max_file_size: Optional[int],
    include_metadata: bool,
    add_tree: bool,
    add_hidden: bool,
    header_only_paths: Set[str],
    header_extensions: Set[str],
):
    project_path = os.path.abspath(project_path)
    output_filepath = os.path.abspath(output_file)

    start_time = time.monotonic()
    files_scanned = 0
    files_included = 0
    files_omitted_header_logic = 0
    total_lines_added = 0

    # Configuración Gitignore
    spec = None
    if use_gitignore:
        actual_gitignore_path = gitignore_path or os.path.join(project_path, ".gitignore")
        if os.path.exists(actual_gitignore_path):
            print(f"Usando reglas de .gitignore desde: {actual_gitignore_path}")
            with open(actual_gitignore_path, "r", encoding="utf-8") as f:
                spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
        else:
            print(f"Advertencia: -g/--use-gitignore activado pero no se encontró '{actual_gitignore_path}'")

    print(f"Analizando proyecto en: {project_path}")
    if header_only_paths:
        print(f"Modo 'Solo Cabeceras' activo para rutas: {', '.join(header_only_paths)}")

    try:
        with open(output_filepath, "w", encoding="utf-8", errors="ignore") as md_file:
            md_file.write(f"# Resumen del Proyecto: {os.path.basename(project_path)}\n\n")

            # 1. Árbol de Directorios
            if add_tree:
                print("Generando árbol de directorios...")
                md_file.write("## Estructura del Proyecto\n\n")
                md_file.write("```\n")
                tree_lines = generate_tree(project_path, project_path, exclude_dirs, spec, add_hidden)
                for line in tree_lines:
                    md_file.write(f"{line}\n")
                md_file.write("```\n\n---\n\n")

            # 2. Recorrido de Archivos
            for root, dirs, files in os.walk(project_path, topdown=True):
                relative_root = os.path.relpath(root, project_path)
                if relative_root == ".":
                    relative_root = ""

                # Filtro 1: Ocultos (Archivos y carpetas que empiezan por '.' se ignoran por defecto)
                if not add_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith(".")]

                # Filtro 2: Exclusiones Manuales y Gitignore
                original_dirs = dirs[:]
                dirs[:] = [d for d in original_dirs if d not in exclude_dirs and not (spec and spec.match_file(os.path.join(relative_root, d).replace(os.sep, "/")))]

                for filename in sorted(files):
                    # Filtro 1 en archivos: Ocultos
                    if not add_hidden and filename.startswith("."):
                        continue

                    files_scanned += 1
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, project_path).replace(os.sep, "/")

                    # Filtro 2: Archivo de salida y Exclusiones Manuales
                    if os.path.abspath(file_path) == output_filepath:
                        continue
                    if filename in exclude_files:
                        continue

                    _, extension = os.path.splitext(filename)
                    if extension.lower() in exclude_extensions:
                        continue

                    # Filtro 3: Gitignore
                    if spec and spec.match_file(relative_path):
                        continue

                    # Filtro 4: Tamaño
                    if max_file_size and os.path.getsize(file_path) > max_file_size:
                        continue

                    # Solo Cabeceras (Header Only)
                    if header_only_paths and is_in_header_path(relative_path, header_only_paths):
                        if not is_header_file(filename, header_extensions):
                            files_omitted_header_logic += 1
                            continue

                    # Procesamiento del contenido
                    if is_text_file(file_path):
                        try:
                            metadata_str = ""
                            if include_metadata:
                                file_size = os.path.getsize(file_path)
                                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                    line_count = sum(1 for _ in f)
                                metadata_str = f"\nSize: {format_bytes(file_size)} | Lines: {line_count}"

                            md_file.write(f"```plaintext\n{relative_path}{metadata_str}\n```\n\n")

                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()

                            total_lines_added += content.count("\n") + 1
                            lang = LANGUAGE_MAP.get(extension.lower(), "")

                            md_file.write(f"```{lang}\n")
                            md_file.write(content.strip())
                            md_file.write(f"\n```\n\n---\n\n")
                            files_included += 1

                        except Exception:
                            pass

        end_time = time.monotonic()
        duration = end_time - start_time
        output_file_size = os.path.getsize(output_filepath)

        print("\n--- Resumen del Proceso ---")
        print(f"✓ ¡Éxito! Resumen guardado en '{output_filepath}'")
        print(f"  - Perfil utilizado: {args.profile if args.profile else 'Ninguno (Default)'}")
        print(f"  - Tiempo total: {duration:.2f} s")
        print(f"  - Tamaño archivo salida: {format_bytes(output_file_size)}")
        print("\n--- Estadísticas ---")
        print(f"  - Archivos escaneados: {files_scanned}")
        print(f"  - Archivos incluidos: {files_included}")
        print(f"  - Omitidos por lógica 'Solo Headers': {files_omitted_header_logic}")
        print(f"  - Líneas agregadas: {total_lines_added}")
        print("----------------------------\n")

    except Exception as e:
        print(f"\nOcurrió un error general: {e}")


# --- PARSEO DE ARGUMENTOS ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Condensador de proyectos a Markdown con perfiles y filtros avanzados.", formatter_class=argparse.RawTextHelpFormatter)

    # --- Argumentos Posicionales ---
    parser.add_argument("project_path", metavar="PROYECTO", help="Ruta al directorio del proyecto.")
    parser.add_argument("output_file", metavar="SALIDA.md", help="Archivo .md de salida.")

    # --- Grupo: Configuración Principal ---
    g_main = parser.add_argument_group("Configuración Principal")
    g_main.add_argument("-p", "--profile", choices=list(PRESETS.keys()), metavar="PERFIL", help="Carga configuración predefinida (stm32, arduino, web, python).")
    g_main.add_argument("-t", "--add-tree", action="store_true", help="Añade árbol de directorios.")
    g_main.add_argument("-m", "--include-metadata", action="store_true", help="Incluye tamaño y líneas de código.")

    # --- Grupo: Filtros y Exclusiones ---
    g_filters = parser.add_argument_group("Filtros y Exclusiones")
    g_filters.add_argument("-H", "--add-hidden", action="store_true", help="Incluye archivos/carpetas ocultas (por defecto se ignoran).")
    g_filters.add_argument("-g", "--use-gitignore", action="store_true", help="Usa reglas de .gitignore.")
    g_filters.add_argument("-gp", "--gitignore-path", metavar="RUTA", help="Ruta alternativa al .gitignore.")

    g_filters.add_argument("-xd", "--exclude-dirs", nargs="+", metavar="DIR", help="Directorios a excluir (se suman al perfil).")
    g_filters.add_argument("-xf", "--exclude-files", nargs="+", metavar="ARCH", help="Archivos a excluir (se suman al perfil).")
    g_filters.add_argument("-xe", "--exclude-extensions", nargs="+", metavar="EXT", help="Extensiones a excluir (ej. .json .log).")
    g_filters.add_argument("-s", "--max-file-size", metavar="TAM", help="Tamaño máx (ej. '100K'). Si hay perfil, se sobrescribe.")

    # --- Grupo: Lógica C/C++ (Header Only) ---
    g_headers = parser.add_argument_group("Modo 'Solo Cabeceras' (Optimización C/C++)")
    g_headers.add_argument("-hp", "--header-only-paths", nargs="+", metavar="RUTA", help="Rutas donde SOLO se incluirán archivos de cabecera/interfaz.")
    g_headers.add_argument("-he", "--header-extensions", nargs="+", metavar="EXT", default=list(DEFAULT_HEADER_EXTS), help="Extensiones consideradas 'headers' (defecto: .h .hpp .d.ts ...)")

    args = parser.parse_args()

    # --- FUSIÓN DE CONFIGURACIÓN (MERGE LOGIC) ---

    # 1. Cargar base (Perfil o Default)
    if args.profile:
        preset = PRESETS[args.profile]
        final_exclude_dirs = set(preset["exclude_dirs"])
        final_exclude_files = set(preset["exclude_files"])
        final_exclude_extensions = set(preset["exclude_extensions"])
        final_max_size_str = args.max_file_size if args.max_file_size else preset["max_file_size"]
    else:
        final_exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)
        final_exclude_files = set(DEFAULT_EXCLUDE_FILES)
        final_exclude_extensions = set(DEFAULT_EXCLUDE_EXTS)
        final_max_size_str = args.max_file_size

    # 2. Sumar argumentos manuales (Aditivo)
    if args.exclude_dirs:
        final_exclude_dirs.update(args.exclude_dirs)
    if args.exclude_files:
        final_exclude_files.update(args.exclude_files)
    if args.exclude_extensions:
        # Asegurar formato .ext
        exts = {ext.lower() if ext.startswith(".") else "." + ext.lower() for ext in args.exclude_extensions}
        final_exclude_extensions.update(exts)

    # 3. Preparar Sets para Header Logic
    final_header_paths = set(args.header_only_paths) if args.header_only_paths else set()
    final_header_exts = {ext.lower() if ext.startswith(".") else "." + ext.lower() for ext in args.header_extensions}

    # Conversión de tamaño
    max_size_bytes = parse_size(final_max_size_str)

    # Ejecución
    generate_project_summary(
        project_path=args.project_path,
        output_file=args.output_file,
        exclude_dirs=final_exclude_dirs,
        exclude_files=final_exclude_files,
        exclude_extensions=final_exclude_extensions,
        use_gitignore=args.use_gitignore,
        gitignore_path=args.gitignore_path,
        max_file_size=max_size_bytes,
        include_metadata=args.include_metadata,
        add_tree=args.add_tree,
        add_hidden=args.add_hidden,
        header_only_paths=final_header_paths,
        header_extensions=final_header_exts,
    )
