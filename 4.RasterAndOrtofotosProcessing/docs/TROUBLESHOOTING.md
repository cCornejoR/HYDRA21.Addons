# HYDRA21 Orthophoto Processor Pro - Guía de Solución de Problemas

## 🚨 **Problemas de Instalación**

### **Error: "Python 3.12 no encontrado"**

**Síntomas**:
```
'python' no se reconoce como un comando interno o externo
```

**Solución**:
1. **Verificar instalación de Python**:
   ```bash
   python --version
   python3 --version
   ```

2. **Instalar Python 3.12**:
   - Descargar desde: https://www.python.org/downloads/
   - ✅ Marcar "Add Python to PATH" durante instalación

3. **Configurar PATH manualmente**:
   ```bash
   # Ejecutar script de configuración
   setup_python312.bat
   ```

### **Error: "GDAL/Rasterio no disponible"**

**Síntomas**:
```
⚠️ Rasterio no disponible - funcionalidad limitada
ImportError: No module named 'rasterio'
```

**Soluciones por orden de preferencia**:

#### **Opción 1: Miniconda (Más Confiable)**
```bash
# 1. Instalar Miniconda
# Descargar: https://docs.conda.io/en/latest/miniconda.html

# 2. Crear entorno
conda create -n hydra21 python=3.12
conda activate hydra21

# 3. Instalar dependencias
conda install -c conda-forge gdal rasterio flet numpy pillow opencv psutil
```

#### **Opción 2: Wheels Pre-compilados**
```bash
# Ejecutar script automático
install_gdal_wheels.bat

# O manualmente:
pip install GDAL-3.8.4-cp312-cp312-win_amd64.whl
pip install rasterio
```

#### **Opción 3: OSGeo4W**
```bash
# 1. Instalar OSGeo4W desde: https://trac.osgeo.org/osgeo4w/
# 2. Seleccionar: GDAL, Python bindings
# 3. Configurar variables de entorno
```

### **Error: "Flet no se puede instalar"**

**Síntomas**:
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solución**:
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar con usuario
pip install --user flet

# O usar conda
conda install -c conda-forge flet
```

---

## 🖥️ **Problemas de Interfaz**

### **Tema no cambia correctamente**

**Síntomas**:
- Botón de tema no responde
- Colores no se actualizan
- Texto ilegible en modo oscuro

**Solución**:
1. **Reiniciar aplicación**:
   ```bash
   # Cerrar completamente y volver a abrir
   python main_professional.py
   ```

2. **Limpiar configuración de tema**:
   ```bash
   # Eliminar archivo de configuración
   del "Documents\HYDRA21-ORTHOPHOTO-PROCESSOR\config\theme_config.json"
   ```

3. **Verificar contraste**:
   - Modo oscuro: Texto blanco sobre fondo oscuro
   - Modo claro: Texto oscuro sobre fondo claro

### **Ventana no se muestra correctamente**

**Síntomas**:
- Ventana muy pequeña o muy grande
- Elementos cortados
- Scroll no funciona

**Solución**:
1. **Restablecer tamaño de ventana**:
   ```python
   # En config/settings.py, verificar:
   "window_width": 1000,
   "window_height": 800
   ```

2. **Verificar resolución de pantalla**:
   - Mínimo recomendado: 1366x768
   - Óptimo: 1920x1080 o superior

3. **Ajustar DPI**:
   - Windows: Configuración > Sistema > Pantalla > Escala

---

## 📁 **Problemas de Archivos**

### **Error: "Archivo no soportado"**

**Síntomas**:
```
❌ Formato de archivo no soportado: .xyz
❌ No se puede leer el archivo
```

**Formatos soportados**:
- ✅ **GeoTIFF**: .tif, .tiff (recomendado)
- ✅ **JPEG**: .jpg, .jpeg
- ✅ **PNG**: .png
- ✅ **Con GDAL**: +200 formatos adicionales

**Solución**:
1. **Convertir formato**:
   ```bash
   # Usar QGIS, ArcGIS, o GDAL para convertir
   gdal_translate input.xyz output.tif
   ```

2. **Verificar integridad**:
   ```bash
   # Verificar que el archivo no esté corrupto
   gdalinfo archivo.tif
   ```

### **Error: "Archivo muy grande"**

**Síntomas**:
```
❌ Error de memoria insuficiente
❌ Procesamiento muy lento
```

**Solución**:
1. **Procesar por chunks**:
   - La aplicación automáticamente divide archivos >2GB
   - Verificar configuración en `config/settings.py`

2. **Aumentar memoria virtual**:
   ```bash
   # Windows: Configuración > Sistema > Acerca de > Configuración avanzada del sistema
   # Aumentar archivo de paginación
   ```

3. **Procesar individualmente**:
   - Seleccionar un archivo a la vez
   - Monitorear uso de RAM

### **Error: "Permisos insuficientes"**

**Síntomas**:
```
❌ PermissionError: [Errno 13] Permission denied
❌ No se puede escribir en el directorio
```

**Solución**:
1. **Ejecutar como administrador**:
   - Clic derecho > "Ejecutar como administrador"

2. **Cambiar directorio de salida**:
   ```bash
   # Usar directorio con permisos de escritura
   Documents\HYDRA21-ORTHOPHOTO-PROCESSOR\output\
   ```

3. **Verificar antivirus**:
   - Agregar excepción para la aplicación
   - Temporalmente deshabilitar protección en tiempo real

---

## ⚡ **Problemas de Rendimiento**

### **Procesamiento muy lento**

**Síntomas**:
- Velocidad <1 MB/s
- CPU <50% de uso
- Tiempo estimado muy alto

**Diagnóstico**:
```bash
# Verificar configuración de CPU
python -c "from config.settings import get_optimal_cpu_count; print(f'CPU cores: {get_optimal_cpu_count()}')"
```

**Solución**:
1. **Verificar configuración de CPU**:
   ```python
   # En config/settings.py
   "max_workers": get_optimal_cpu_count(),  # Debe usar 75% de núcleos
   ```

2. **Optimizar almacenamiento**:
   - Usar SSD en lugar de HDD
   - Separar archivos de entrada y salida en discos diferentes

3. **Cerrar aplicaciones innecesarias**:
   - Liberar RAM y CPU
   - Verificar en Task Manager

### **Alto uso de memoria**

**Síntomas**:
```
❌ MemoryError: Unable to allocate array
RAM >90% de uso
```

**Solución**:
1. **Reducir tamaño de chunk**:
   ```python
   # En config/settings.py
   "chunk_size": 512,  # Reducir de 1024 a 512 MB
   ```

2. **Procesar menos archivos simultáneamente**:
   - Seleccionar 1-5 archivos a la vez
   - Procesar en lotes pequeños

3. **Aumentar memoria virtual**:
   - Windows: Configuración del archivo de paginación
   - Recomendado: 2x la RAM física

### **CPU no se utiliza completamente**

**Síntomas**:
- CPU <50% durante procesamiento
- Un solo núcleo al 100%
- Otros núcleos inactivos

**Solución**:
1. **Verificar configuración de threading**:
   ```python
   # Verificar que max_workers > 1
   print(f"Workers configurados: {PROCESSING_CONFIG['max_workers']}")
   ```

2. **Actualizar configuración GDAL**:
   ```bash
   # Variables de entorno
   set GDAL_NUM_THREADS=ALL_CPUS
   set OMP_NUM_THREADS=6  # Número de núcleos disponibles
   ```

3. **Verificar tipo de archivo**:
   - Archivos muy pequeños no se benefician del paralelismo
   - Usar archivos >50MB para mejor paralelización

---

## 🔧 **Problemas de Configuración**

### **Configuración no se guarda**

**Síntomas**:
- Configuraciones se pierden al reiniciar
- Tema vuelve al predeterminado
- Directorio de salida se resetea

**Solución**:
1. **Verificar permisos de escritura**:
   ```bash
   # Directorio de configuración
   Documents\HYDRA21-ORTHOPHOTO-PROCESSOR\config\
   ```

2. **Recrear archivos de configuración**:
   ```bash
   # Eliminar configuración corrupta
   del "Documents\HYDRA21-ORTHOPHOTO-PROCESSOR\config\*.json"
   
   # Reiniciar aplicación para regenerar
   python main_professional.py
   ```

### **Directorio de salida no se crea**

**Síntomas**:
```
❌ No se puede crear directorio de salida
❌ FileNotFoundError: [Errno 2] No such file or directory
```

**Solución**:
1. **Verificar ruta**:
   ```python
   # Verificar que la ruta sea válida
   from pathlib import Path
   output_dir = Path("Documents/HYDRA21-ORTHOPHOTO-PROCESSOR/output")
   print(f"Existe: {output_dir.exists()}")
   ```

2. **Crear manualmente**:
   ```bash
   mkdir "Documents\HYDRA21-ORTHOPHOTO-PROCESSOR\output"
   ```

3. **Cambiar ubicación**:
   - Usar directorio con permisos garantizados
   - Evitar rutas con espacios o caracteres especiales

---

## 📊 **Problemas de Resultados**

### **Archivos de salida corruptos**

**Síntomas**:
- No se pueden abrir en GIS
- Tamaño 0 bytes
- Error de formato

**Solución**:
1. **Verificar espacio en disco**:
   ```bash
   # Verificar espacio libre
   dir "Documents\HYDRA21-ORTHOPHOTO-PROCESSOR\output"
   ```

2. **No interrumpir procesamiento**:
   - Esperar a que termine completamente
   - No cerrar la aplicación durante procesamiento

3. **Usar compresión sin pérdida**:
   - Para archivos críticos usar "Sin pérdida"
   - Verificar integridad con QGIS/ArcGIS

### **Metadatos perdidos**

**Síntomas**:
- CRS no preservado
- Georreferenciación perdida
- Metadatos vacíos

**Solución**:
1. **Activar preservación de CRS**:
   ```python
   # En opciones de procesamiento
   preserve_crs=True
   ```

2. **Usar perfil GIS**:
   - Seleccionar "Análisis GIS" en opciones
   - Evitar perfiles "Web" o "Móvil" para datos críticos

3. **Verificar archivo original**:
   ```bash
   # Verificar que el archivo original tenga metadatos
   gdalinfo archivo_original.tif
   ```

---

## 🆘 **Obtener Ayuda Adicional**

### **Generar Reporte de Diagnóstico**

```bash
# Ejecutar diagnóstico completo
python test_comprehensive_improvements.py > diagnostico.txt
```

### **Información del Sistema**

```bash
# Información detallada del sistema
python -c "
import sys, platform, psutil
print(f'Python: {sys.version}')
print(f'OS: {platform.system()} {platform.release()}')
print(f'CPU: {psutil.cpu_count()} cores')
print(f'RAM: {psutil.virtual_memory().total // (1024**3)} GB')
"
```

### **Logs de Error**

**Ubicación**:
```
Documents\HYDRA21-ORTHOPHOTO-PROCESSOR\logs\
```

**Incluir en reportes**:
- Archivo de log más reciente
- Configuración del sistema
- Pasos para reproducir el error
- Archivos de ejemplo (si es posible)

### **Contacto**

- **GitHub Issues**: https://github.com/cCornejoR/HYDRA21.Addons/issues
- **Documentación**: `docs/USER_MANUAL.md`
- **Tests**: `test_app.py`, `test_comprehensive_improvements.py`

---

*Guía de Solución de Problemas - HYDRA21 Orthophoto Processor Pro v1.0*
