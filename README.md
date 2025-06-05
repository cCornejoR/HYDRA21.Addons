# HYDRA21 PDF Compressor & Clipboard Manager

Esta aplicación incluye dos componentes principales:

- HYDRA21 PDF Compressor: Una herramienta para comprimir archivos PDF
- HYDRA21 Clipboard Manager: Una herramienta para gestionar el portapapeles
- HYDRA21 PaperTranslateIA: Una herramienta para traducir documentos (en progreso)

## Project Structure

This repository contains multiple Python projects:

- **`1.Clipboard-Extension (ok-v0.0.1)/`**: A clipboard management tool.
- **`2.PDF-Extensión (ok-v0.5.0)/`**: A tool for compressing PDF files.
- **`3.PaperTranslateIA-Extension (progress)/`**: An extension for AI-powered paper translation (currently in progress).

## Requisitos

- Python 3.8 o superior
- Ghostscript (para el compresor PDF)

## Instalación

1. Clone este repositorio:

   ```
   git clone https://github.com/yourusername/HYDRA21_APP.git
   ```

2. Instale las dependencias.

   - For general dependencies:
     ```
     pip install -r requirements.txt
     ```
   - For the PDF Compressor:
     ```
     pip install -r "2.PDF-Extensión (ok-v0.5.0)/requirements.txt"
     ```
   - For the Clipboard Manager: No specific `requirements.txt` file. General dependencies should cover it.
   - For the PaperTranslateIA-Extension:
     ```
     pip install -r "3.PaperTranslateIA-Extension (progress)/requirements_improved.txt"
     ```

3. Para el compresor PDF, asegúrese de tener Ghostscript instalado:
   - Windows: Descargue e instale desde [ghostscript.com](https://www.ghostscript.com/download/gsdnld.html)
   - Linux: `sudo apt-get install ghostscript`
   - macOS: `brew install ghostscript`

## Uso

### PDF Compressor

Para iniciar el compresor PDF:

```bash
cd "2.PDF-Extensión (ok-v0.5.0)"
python main_professional.py
```

### Clipboard Manager

Para iniciar el gestor de portapapeles:

```bash
cd "1.Clipboard-Extension (ok-v0.0.1)"
python main.py
```

### PaperTranslateIA-Extension

Para iniciar el traductor de documentos (actualmente en desarrollo):

```bash
cd "3.PaperTranslateIA-Extension (progress)"
python main_improved.py
```

_(Note: Assuming `main_improved.py` is the correct entry point based on `ls` output showing `main_fixed.py` and `main_improved.py`)_

## Características

### PDF Compressor

- Interfaz moderna y compacta
- Diferentes niveles de compresión
- Estadísticas de reducción de tamaño
- Tema claro/oscuro

### Clipboard Manager

- Registro histórico de portapapeles
- Fácil acceso a elementos copiados anteriormente
- Interfaz intuitiva

### PaperTranslateIA-Extension

- (Características por definir según avance el desarrollo)

## Configuración

Los archivos de configuración se encuentran en:

- PDF Compressor: `2.PDF-Extensión (ok-v0.5.0)/config/` (contiene `settings.py`, `ghostscript_config.py`, etc.)
- Clipboard Manager: (No specific configuration files mentioned, assume none for now)
- PaperTranslateIA-Extension: (No specific configuration files mentioned, assume none for now)

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
