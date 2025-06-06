# HYDRA21 Orthophoto Processor Pro - Manual de Usuario Completo

## 📋 **Tabla de Contenidos**

1. [Introducción](#introducción)
2. [Instalación y Configuración](#instalación-y-configuración)
3. [Interfaz de Usuario](#interfaz-de-usuario)
4. [Guía de Uso Paso a Paso](#guía-de-uso-paso-a-paso)
5. [Configuraciones Avanzadas](#configuraciones-avanzadas)
6. [Solución de Problemas](#solución-de-problemas)
7. [Casos de Uso Específicos](#casos-de-uso-específicos)
8. [Optimización de Rendimiento](#optimización-de-rendimiento)

---

## 🎯 **Introducción**

HYDRA21 Orthophoto Processor Pro es una aplicación profesional para el procesamiento de ortofotos y datos geoespaciales. Diseñada para profesionales en GIS, topografía, y teledetección, ofrece herramientas avanzadas para:

- **Compresión inteligente** de ortofotos con múltiples algoritmos
- **Procesamiento geoespacial** con preservación de metadatos
- **Optimización automática** de CPU y memoria
- **Interfaz profesional** con indicadores de progreso en tiempo real
- **Soporte para múltiples formatos** geoespaciales

### **Características Principales**

✅ **Compresión Avanzada**: 4+ métodos de compresión (Rasterio, OpenCV, Pillow, GDAL)  
✅ **Geoespacial Nativo**: Soporte completo para CRS, proyecciones y metadatos  
✅ **Procesamiento Paralelo**: Uso optimizado del 75% de núcleos de CPU  
✅ **Progreso en Tiempo Real**: Indicadores detallados con ETA y estadísticas  
✅ **Temas Profesionales**: Modo claro/oscuro con excelente contraste  

---

## 🔧 **Instalación y Configuración**

### **Requisitos del Sistema**

- **Sistema Operativo**: Windows 10/11 (64-bit)
- **Python**: 3.12 o superior
- **RAM**: Mínimo 4GB, recomendado 8GB+
- **Espacio en Disco**: 2GB libres para instalación
- **CPU**: Procesador multi-núcleo recomendado

### **Instalación Básica**

1. **Descargar la aplicación**:
   ```bash
   git clone https://github.com/cCornejoR/HYDRA21.Addons.git
   cd "4.RasterAndOrtofotosProcessing"
   ```

2. **Configurar Python 3.12**:
   ```bash
   # Ejecutar script de configuración
   setup_python312.bat
   ```

3. **Instalar dependencias básicas**:
   ```bash
   pip install flet numpy pillow opencv-python psutil
   ```

### **Instalación Completa con GDAL/Rasterio**

Para funcionalidad geoespacial completa:

1. **Opción A - Miniconda (Recomendada)**:
   ```bash
   # Instalar Miniconda desde: https://docs.conda.io/en/latest/miniconda.html
   conda create -n hydra21 python=3.12
   conda activate hydra21
   conda install -c conda-forge gdal rasterio flet numpy pillow opencv psutil
   ```

2. **Opción B - Wheels Pre-compilados**:
   ```bash
   # Ejecutar script automático
   install_gdal_wheels.bat
   ```

### **Verificación de Instalación**

```bash
# Ejecutar test de la aplicación
python test_app.py
```

**Salida esperada**:
```
✅ Flet disponible
✅ NumPy disponible  
✅ Pillow disponible
✅ OpenCV disponible
✅ Rasterio disponible (opcional)
🎉 4 métodos de compresión detectados
```

---

## 🖥️ **Interfaz de Usuario**

### **Diseño General**

La aplicación utiliza una **interfaz con pestañas** profesional:

1. **📁 Archivos** - Selección y gestión de archivos
2. **⚙️ Opciones** - Configuración de procesamiento  
3. **📊 Progreso** - Monitoreo en tiempo real
4. **📋 Resultados** - Análisis de resultados

### **Barra Superior**

- **🏠 Inicio**: Volver a la pantalla principal
- **❓ Ayuda**: Manual y tutoriales
- **ℹ️ Acerca de**: Información de la aplicación
- **🌙/☀️ Tema**: Cambio entre modo claro/oscuro

### **Indicadores de Estado**

- **🟢 Verde**: Operación exitosa
- **🟡 Amarillo**: Advertencia o en progreso
- **🔴 Rojo**: Error o fallo
- **🔵 Azul**: Información general

---

## 📖 **Guía de Uso Paso a Paso**

### **Paso 1: Seleccionar Archivos**

1. **Ir a la pestaña "Archivos"**
2. **Hacer clic en "Seleccionar Archivos"**
3. **Elegir ortofotos** (formatos soportados: .tif, .tiff, .jpg, .png)
4. **Verificar la lista** de archivos seleccionados

**Formatos Soportados**:
- **GeoTIFF** (.tif, .tiff) - Recomendado para datos geoespaciales
- **JPEG** (.jpg, .jpeg) - Para imágenes comprimidas
- **PNG** (.png) - Para imágenes con transparencia
- **Otros**: Según disponibilidad de GDAL/Rasterio

### **Paso 2: Configurar Opciones**

1. **Ir a la pestaña "Opciones"**
2. **Seleccionar perfil de exportación**:
   - **🗺️ Análisis GIS**: Máxima calidad para análisis
   - **📊 Cartografía**: Optimizado para mapas
   - **🌐 Web**: Optimizado para visualización web
   - **📱 Móvil**: Tamaño reducido para dispositivos móviles

3. **Configurar compresión**:
   - **Sin pérdida**: Máxima calidad, mayor tamaño
   - **Alta calidad**: Excelente balance calidad/tamaño
   - **Calidad media**: Buena compresión, calidad aceptable
   - **Calidad básica**: Máxima compresión, calidad mínima

4. **Opciones avanzadas**:
   - **Preservar CRS**: Mantener sistema de coordenadas
   - **Crear overviews**: Generar pirámides para visualización rápida
   - **Calidad JPEG**: 1-100 (solo para compresión JPEG)

### **Paso 3: Iniciar Procesamiento**

1. **Hacer clic en "Iniciar Procesamiento"**
2. **Automáticamente cambia a pestaña "Progreso"**
3. **Monitorear el progreso en tiempo real**:
   - Barra de progreso general
   - Archivo actual en procesamiento
   - Tiempo estimado restante (ETA)
   - Estadísticas de compresión

### **Paso 4: Revisar Resultados**

1. **Al completar, automáticamente va a "Resultados"**
2. **Revisar estadísticas**:
   - Archivos procesados exitosamente
   - Archivos con errores
   - Ratio de compresión total
   - Tiempo de procesamiento
   - Velocidad promedio

3. **Acciones disponibles**:
   - **Abrir carpeta de salida**
   - **Ver detalles de cada archivo**
   - **Exportar reporte**
   - **Procesar más archivos**

---

## ⚙️ **Configuraciones Avanzadas**

### **Optimización de CPU**

La aplicación **automáticamente detecta** y usa el 75% de los núcleos de CPU disponibles:

```python
# Configuración automática
Total de núcleos: 8
Núcleos utilizados: 6 (75%)
```

**Para ajustar manualmente**:
1. Editar `config/settings.py`
2. Modificar `cpu_usage_percentage`
3. Reiniciar la aplicación

### **Gestión de Memoria**

**Configuración automática**:
- **Uso máximo de RAM**: 80% de la disponible
- **Tamaño de chunk**: 1024 MB
- **Cache intermedio**: 128 MB

**Para archivos muy grandes** (>2GB):
- La aplicación automáticamente usa procesamiento por chunks
- Reduce el uso de memoria manteniendo la calidad

### **Perfiles de Exportación Personalizados**

Crear perfiles personalizados editando `config/orthophoto_config.py`:

```python
"mi_perfil_custom": {
    "name": "Mi Perfil Personalizado",
    "description": "Configuración específica",
    "format": "GTiff",
    "compression": "LZW",
    "quality": 90,
    "tile_size": 512,
    "overview_levels": [2, 4, 8, 16],
    "world_file": True
}
```

---

## 🔧 **Solución de Problemas**

### **Problemas Comunes**

#### **❌ "Rasterio no disponible"**
**Causa**: GDAL/Rasterio no instalado  
**Solución**:
```bash
# Instalar con conda (recomendado)
conda install -c conda-forge rasterio

# O usar wheels pre-compilados
install_gdal_wheels.bat
```

#### **❌ "Error de memoria insuficiente"**
**Causa**: Archivos muy grandes para la RAM disponible  
**Solución**:
1. Procesar archivos de uno en uno
2. Reducir `chunk_size` en configuración
3. Cerrar otras aplicaciones

#### **❌ "Archivo de salida corrupto"**
**Causa**: Interrupción durante procesamiento  
**Solución**:
1. Verificar espacio en disco suficiente
2. No interrumpir el procesamiento
3. Usar compresión "Sin pérdida" para archivos críticos

#### **❌ "Procesamiento muy lento"**
**Causa**: Configuración subóptima  
**Solución**:
1. Verificar que se usen múltiples núcleos de CPU
2. Usar SSD en lugar de HDD
3. Aumentar RAM disponible

### **Logs y Diagnóstico**

**Ubicación de logs**:
```
Documents/HYDRA21-ORTHOPHOTO-PROCESSOR/logs/
```

**Niveles de log**:
- **INFO**: Información general
- **WARNING**: Advertencias
- **ERROR**: Errores recuperables  
- **CRITICAL**: Errores críticos

**Para diagnóstico avanzado**:
```bash
# Ejecutar con verbose
python main_professional.py --verbose

# Test de funcionalidad
python test_comprehensive_improvements.py
```

---

## 🎯 **Casos de Uso Específicos**

### **Caso 1: Procesamiento de Ortofotos para GIS**

**Objetivo**: Preparar ortofotos para análisis en QGIS/ArcGIS

**Configuración recomendada**:
- **Perfil**: Análisis GIS
- **Compresión**: Sin pérdida o Alta calidad
- **Preservar CRS**: ✅ Activado
- **Crear overviews**: ✅ Activado

**Flujo de trabajo**:
1. Seleccionar ortofotos GeoTIFF originales
2. Configurar perfil "Análisis GIS"
3. Mantener compresión LZW o DEFLATE
4. Procesar con preservación de metadatos
5. Verificar CRS en software GIS

### **Caso 2: Optimización para Visualización Web**

**Objetivo**: Reducir tamaño para mapas web

**Configuración recomendada**:
- **Perfil**: Web
- **Compresión**: Calidad media
- **Formato**: JPEG con calidad 85
- **Crear overviews**: ✅ Activado

**Flujo de trabajo**:
1. Seleccionar ortofotos de alta resolución
2. Configurar perfil "Web"
3. Ajustar calidad JPEG según necesidades
4. Procesar con generación de pirámides
5. Verificar tamaño final vs. calidad visual

### **Caso 3: Archivo Masivo de Ortofotos**

**Objetivo**: Procesar cientos de ortofotos eficientemente

**Configuración recomendada**:
- **Procesamiento por lotes**: Grupos de 10-20 archivos
- **Compresión**: Alta calidad
- **Monitoreo**: Activar todas las estadísticas
- **CPU**: Usar configuración automática (75%)

**Flujo de trabajo**:
1. Organizar archivos por tamaño/tipo
2. Procesar en lotes pequeños
3. Monitorear uso de memoria y CPU
4. Verificar resultados de cada lote
5. Consolidar reportes finales

---

## ⚡ **Optimización de Rendimiento**

### **Configuración de Hardware**

**CPU**:
- **Recomendado**: 6+ núcleos físicos
- **Configuración**: 75% de núcleos (automático)
- **Monitoreo**: Task Manager durante procesamiento

**Memoria RAM**:
- **Mínimo**: 8GB para archivos <500MB
- **Recomendado**: 16GB+ para archivos >1GB
- **Configuración**: 80% de RAM disponible (automático)

**Almacenamiento**:
- **Recomendado**: SSD para archivos temporales
- **Espacio libre**: 3x el tamaño de archivos a procesar
- **Ubicación**: Separar entrada y salida en discos diferentes

### **Configuración de Software**

**Variables de entorno GDAL**:
```bash
GDAL_CACHEMAX=512          # Cache de 512MB
GDAL_NUM_THREADS=ALL_CPUS  # Usar todos los núcleos
VSI_CACHE=TRUE             # Activar cache virtual
```

**Configuración de Python**:
```bash
# Usar Python 3.12 para mejor rendimiento
python --version  # Verificar versión
```

### **Monitoreo de Rendimiento**

**Durante el procesamiento, monitorear**:
- **CPU**: Debe estar al 75% de uso
- **RAM**: No debe superar el 80%
- **Disco**: Actividad de lectura/escritura constante
- **Temperatura**: CPU <80°C

**Indicadores de problemas**:
- CPU <50%: Posible cuello de botella de disco
- RAM >90%: Reducir tamaño de chunk
- Disco 100%: Usar SSD o reducir archivos simultáneos

---

## 📞 **Soporte y Contacto**

**Documentación adicional**:
- `docs/GDAL_RASTERIO_ANALYSIS.md` - Análisis técnico detallado
- `docs/TROUBLESHOOTING.md` - Guía de solución de problemas
- `README.md` - Información general del proyecto

**Reportar problemas**:
- GitHub Issues: [Crear nuevo issue](https://github.com/cCornejoR/HYDRA21.Addons/issues)
- Incluir logs de error y configuración del sistema

**Actualizaciones**:
- Verificar regularmente el repositorio para nuevas versiones
- Leer CHANGELOG.md para cambios importantes

---

*HYDRA21 Orthophoto Processor Pro v1.0 - Manual de Usuario*  
*Última actualización: Diciembre 2024*
