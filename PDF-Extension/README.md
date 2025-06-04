# 🚀 HYDRA21 PDF Compressor Pro

Una aplicación profesional de procesamiento de PDFs con interfaz moderna desarrollada con Flet (Flutter para Python).

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Características Principales

### 📦 Compresión de PDFs
- **Múltiples niveles de calidad**: Alta, Media, Baja
- **Compresión por lotes**: Procesa múltiples archivos simultáneamente
- **Estadísticas detalladas**: Ratios de compresión, tiempo de procesamiento
- **Preservación de calidad**: Algoritmos optimizados para mantener legibilidad

### 🔗 Fusión de PDFs
- **Combinación inteligente**: Une múltiples PDFs en uno solo
- **Orden personalizable**: Reorganiza archivos antes de fusionar
- **Validación automática**: Verifica integridad de archivos

### ✂️ División de PDFs
- **Extracción por páginas**: Especifica rangos de páginas exactos
- **División automática**: Separa por capítulos o secciones
- **Nomenclatura inteligente**: Nombres de archivo descriptivos

### 🎨 Interfaz Moderna
- **Tema azul elegante**: Diseño sin sombras (preferencia del usuario)
- **Modo claro/oscuro**: Cambio dinámico de tema
- **Indicadores de progreso**: Spinners y barras de progreso visibles
- **Acceso directo**: Botones para abrir archivos y carpetas

## 🛠️ Instalación

### Requisitos Previos
- **Python 3.8+**
- **Ghostscript** (se puede instalar automáticamente)

### Instalación Automática
```bash
# Clona el repositorio
git clone https://github.com/cCornejoR/HYDRA21.Addons.git
cd HYDRA21.Addons/PDF-Extension

# Ejecuta el instalador
python install.py
```

### Instalación Manual
```bash
# Instala dependencias
pip install -r requirements.txt

# Ejecuta la aplicación
python main.py
```

## 🚀 Uso Rápido

### Primera Ejecución
1. **Ejecuta la aplicación**: `python main.py`
2. **Sigue el tutorial**: Configuración automática de Ghostscript
3. **Selecciona archivos**: Usa el selector de archivos integrado
4. **Procesa**: Elige operación (comprimir/fusionar/dividir)
5. **Revisa resultados**: Estadísticas detalladas y acceso directo

### Operaciones Principales

#### Compresión
```
1. Selecciona archivos PDF
2. Elige nivel de calidad (Alta/Media/Baja)
3. Haz clic en "Comprimir PDFs"
4. Revisa estadísticas de compresión
```

#### Fusión
```
1. Selecciona múltiples PDFs
2. Organiza el orden si es necesario
3. Haz clic en "Fusionar PDFs"
4. Obtén un archivo PDF combinado
```

#### División
```
1. Selecciona un PDF
2. Especifica rango de páginas
3. Haz clic en "Dividir PDF"
4. Obtén archivos separados
```

## ⚙️ Configuración

### Ghostscript
La aplicación requiere Ghostscript para procesar PDFs:

- **Windows**: Descarga desde [ghostscript.com](https://www.ghostscript.com/download/gsdnld.html)
- **Linux**: `sudo apt-get install ghostscript`
- **macOS**: `brew install ghostscript`

### Configuración Avanzada
- **Calidad personalizada**: Modifica presets en `config/settings.py`
- **Directorios**: Personaliza rutas de salida y temporales
- **Temas**: Ajusta colores en `ui/themes/theme_manager.py`

## 📊 Características Técnicas

### Arquitectura
```
PDF-Extension/
├── main.py              # Punto de entrada
├── config/              # Configuraciones
├── core/                # Lógica de procesamiento
├── ui/                  # Interfaz de usuario
│   ├── components/      # Componentes reutilizables
│   └── themes/          # Gestión de temas
└── utils/               # Utilidades
```

### Tecnologías
- **Flet**: Framework UI (Flutter para Python)
- **Ghostscript**: Motor de procesamiento PDF
- **PyPDF2**: Manipulación de PDFs
- **Pydantic**: Validación de datos
- **Threading**: Procesamiento asíncrono

## 🎯 Características Destacadas

### Indicadores de Progreso
- ✅ **Spinners visibles** durante procesamiento
- ✅ **Barras de progreso** con porcentajes exactos
- ✅ **Estadísticas en tiempo real** (archivos procesados, tiempo restante)
- ✅ **Estados de error** claramente identificados

### Estadísticas Completas
- 📈 **Ratios de compresión** detallados
- ⏱️ **Tiempos de procesamiento** por archivo y total
- 📁 **Rutas de archivos** de entrada y salida
- 💾 **Tamaños de archivo** antes y después

### Acceso Directo
- 🔗 **Botones "Abrir Archivo"** para resultados
- 📂 **Botones "Abrir Carpeta"** para navegación rápida
- 🎯 **Integración con explorador** del sistema

## 🐛 Solución de Problemas

### Errores Comunes

**Ghostscript no encontrado**
```
Solución: Instala Ghostscript o especifica la ruta manualmente
```

**Error de permisos**
```
Solución: Ejecuta como administrador o cambia directorio de salida
```

**Archivos muy grandes**
```
Solución: Ajusta límite en config/settings.py (MAX_FILE_SIZE_MB)
```

### Logs y Depuración
- Los logs se guardan en `logs/app.log`
- Modo debug disponible en configuración
- Reportes de error automáticos

## 🤝 Contribución

### Desarrollo
```bash
# Fork del repositorio
git clone https://github.com/tu-usuario/HYDRA21.Addons.git

# Crea rama de feature
git checkout -b feature/nueva-funcionalidad

# Desarrolla y prueba
python -m pytest tests/

# Commit y push
git commit -m "Añade nueva funcionalidad"
git push origin feature/nueva-funcionalidad
```

### Reportar Bugs
1. Usa el sistema de Issues de GitHub
2. Incluye logs y pasos para reproducir
3. Especifica versión de Python y SO

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Créditos

- **Desarrollado por**: HYDRA21 Team
- **Framework UI**: Flet (Flutter para Python)
- **Motor PDF**: Ghostscript
- **Inspiración**: Necesidad de herramientas PDF profesionales

---

**¿Necesitas ayuda?** Abre un issue o contacta al equipo de desarrollo.

**¿Te gusta el proyecto?** ⭐ Dale una estrella en GitHub!
