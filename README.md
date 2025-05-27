# HYDRA21 PDF Compressor & Clipboard Manager

Esta aplicación incluye dos componentes principales:
- HYDRA21 PDF Compressor: Una herramienta para comprimir archivos PDF
- HYDRA21 Clipboard Manager: Una herramienta para gestionar el portapapeles

## Requisitos

- Python 3.8 o superior
- Ghostscript (para el compresor PDF)
- Bibliotecas de Python listadas en `requirements.txt`

## Instalación

1. Clone este repositorio:
   ```
   git clone https://github.com/yourusername/HYDRA21_APP.git
   ```

2. Instale las dependencias:
   ```
   pip install -r PDF-Extension/requirements.txt
   ```

3. Para el compresor PDF, asegúrese de tener Ghostscript instalado:
   - Windows: Descargue e instale desde [ghostscript.com](https://www.ghostscript.com/download/gsdnld.html)
   - Linux: `sudo apt-get install ghostscript`
   - macOS: `brew install ghostscript`

## Uso

### PDF Compressor

Para iniciar el compresor PDF:

```bash
cd PDF-Extension
python main_flet.py
```

### Clipboard Manager

Para iniciar el gestor de portapapeles:

```bash
cd Clipboard-Extension
python main.py
```

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

## Configuración

Los archivos de configuración se encuentran en:
- `PDF-Extension/config.json`

## Licencia

© 2024 HYDRA21
