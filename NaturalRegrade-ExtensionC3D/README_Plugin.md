# Natural Regrade Extension for Civil 3D

## Descripción

El plugin **Natural Regrade** es una extensión avanzada para Autodesk Civil 3D que implementa técnicas de análisis geomorfológico para crear superficies naturales resistentes a la erosión. Basado en la metodología científica de GeoFluv Inc. y principios de diseño geomorfológico, este plugin es ideal para proyectos de cierre minero y restauración de paisajes.

## Características Principales

### 🌊 Análisis Hidrológico Avanzado
- **Algoritmo D8**: Cálculo preciso de direcciones de flujo superficial
- **Acumulación de Flujo**: Identificación automática de cursos de agua naturales
- **Análisis de Cuencas**: Delimitación de áreas de drenaje

### 🏞️ Generación de Redes de Drenaje
- **Líneas de Drenaje Naturales**: Creación automática de cursos de agua siguiendo principios fluviales
- **Orden de Strahler**: Clasificación jerárquica de la red hidrográfica
- **Morfología Fluvial**: Aplicación de sinuosidad y meandering natural

### 🎯 Suavizado Geomorfológico
- **Filtros Laplacianos**: Suavizado preservando características topográficas críticas
- **Filtros Gaussianos**: Transiciones suaves y naturales
- **Suavizado Adaptativo**: Ajuste automático basado en rugosidad local
- **Preservación de Drenaje**: Mantenimiento de líneas de agua durante el procesamiento

### 🔧 Validación y Optimización
- **Análisis de Estabilidad**: Verificación de pendientes para resistencia a erosión
- **Validación de Flujo**: Asegurar drenaje correcto hacia cursos de agua
- **Estadísticas Detalladas**: Métricas completas del procesamiento

## Interfaz de Usuario

### Diseño Moderno y Profesional
- **Material Design**: Interfaz moderna siguiendo principios de Google Material Design
- **Controles Intuitivos**: Sliders, checkboxes y campos de texto claramente organizados
- **Vista Previa de Parámetros**: Resumen completo antes de ejecutar
- **Validación en Tiempo Real**: Verificación automática de parámetros

### Secciones Principales
1. **Selección de Superficie**: Elección de superficie TIN a procesar
2. **Parámetros Hidrológicos**: Configuración del análisis de flujo
3. **Parámetros de Suavizado**: Control del proceso de suavizado geomorfológico
4. **Configuración de Salida**: Nombres y opciones de resultados

## Comandos Disponibles

### `NATURALREGRADE`
Comando principal que ejecuta el análisis completo de regrade geomorfológico.

**Uso:**
```
NATURALREGRADE
```

### `NATURALREGRADE_INFO`
Muestra información detallada del plugin y sus capacidades.

**Uso:**
```
NATURALREGRADE_INFO
```

## Fundamento Científico

Este plugin está basado en investigación científica reconocida internacionalmente:

### Referencias Principales
- **Bugosh & Eckels (2025)** - GeoFluv Inc. - Metodología de diseño geomorfológico
- **Bugosh & Epp (2019)** - Catena - Principios de estabilidad en diseño de paisajes
- **Hancock et al. (2018)** - Environmental Modelling and Software - Algoritmos de evolución del paisaje
- **Zapico et al. (2018)** - Ecological Engineering - Diseño de sistemas de drenaje naturales
- **Zhang et al. (2018)** - ASMR Proceedings - Validación de resistencia a erosión
- **Duque & Bugosh (2016-2012)** - Gecamin, CIUDEN - Aplicaciones en cierre minero

### Metodología GeoFluv
El plugin implementa los principios fundamentales de GeoFluv:
- **Diseño Basado en Fluvial Geomorfología**: Replicación de patrones naturales de erosión y deposición
- **Estabilidad Dinámica**: Creación de paisajes que evolucionan naturalmente sin degradación
- **Resistencia a Erosión**: Superficies diseñadas para minimizar la erosión a largo plazo
- **Funcionalidad Hidrológica**: Sistemas de drenaje eficientes y naturales

## Parámetros de Configuración

### Parámetros Hidrológicos
- **Resolución de Malla**: 1-20 metros (menor valor = mayor detalle)
- **Acumulación Mínima**: 10-1000 (umbral para identificar cursos de agua)
- **Buffer de Drenaje**: Distancia de protección alrededor de líneas de agua

### Parámetros de Suavizado
- **Factor de Suavizado**: 0.1-1.0 (intensidad del suavizado)
- **Iteraciones**: 1-20 (número de pasadas del filtro)
- **Pendiente Máxima**: 15-45° (límite de estabilidad geotécnica)
- **Preservar Drenaje**: Mantener líneas de agua intactas
- **Suavizado Adaptativo**: Ajuste automático según rugosidad

### Configuración de Salida
- **Superficie Resultado**: Nombre de la nueva superficie TIN
- **Capa de Drenaje**: Nombre de la capa para líneas de drenaje
- **Contornos**: Generación automática de curvas de nivel
- **Validación**: Verificación de resistencia a erosión
- **Reportes**: Generación de estadísticas detalladas

## Aplicaciones Típicas

### 🏭 Cierre de Minas
- Diseño de escombreras estables
- Restauración de cortas mineras
- Rehabilitación de áreas de procesamiento

### 🌱 Restauración Ambiental
- Rehabilitación de paisajes degradados
- Diseño de humedales artificiales
- Restauración de cauces naturales

### 🏗️ Ingeniería Civil
- Diseño de taludes estables
- Sistemas de drenaje natural
- Proyectos de infraestructura sostenible

## Requisitos del Sistema

### Software Requerido
- **Autodesk Civil 3D 2023** o superior
- **.NET Framework 9.0** o superior
- **Windows 10/11** (64-bit)

### Hardware Recomendado
- **RAM**: Mínimo 8 GB, recomendado 16 GB
- **Procesador**: Intel i5 o equivalente AMD
- **Espacio en Disco**: 100 MB para instalación
- **Gráficos**: Tarjeta compatible con DirectX 11

## Instalación

1. **Copiar Archivos**: Colocar el archivo .dll compilado en la carpeta de plugins de Civil 3D
2. **Cargar Plugin**: Usar comando `NETLOAD` en Civil 3D para cargar el plugin
3. **Verificar Instalación**: Ejecutar `NATURALREGRADE_INFO` para confirmar carga exitosa

## Flujo de Trabajo Típico

1. **Abrir Civil 3D** con superficie TIN existente
2. **Ejecutar Comando** `NATURALREGRADE`
3. **Seleccionar Superficie** TIN a procesar
4. **Configurar Parámetros** según requisitos del proyecto
5. **Vista Previa** de configuración (opcional)
6. **Ejecutar Procesamiento** y esperar resultados
7. **Revisar Resultados** - nueva superficie y red de drenaje
8. **Validar Salida** usando estadísticas y visualización

## Resultados Esperados

### Productos Generados
- **Nueva Superficie TIN**: Versión suavizada y geomorfológicamente optimizada
- **Red de Drenaje**: Líneas de flujo naturales como polilíneas
- **Curvas de Nivel**: Contornos automáticos (opcional)
- **Estadísticas**: Métricas detalladas del procesamiento

### Beneficios Obtenidos
- **Estabilidad a Largo Plazo**: Reducción significativa de erosión
- **Apariencia Natural**: Paisajes que se integran con el entorno
- **Funcionalidad Hidrológica**: Drenaje eficiente sin mantenimiento
- **Cumplimiento Normativo**: Diseños que cumplen estándares ambientales

## Soporte Técnico

### Desarrollado por
**Hydra21 Solutions**
- Especialistas en tecnología geomorfológica
- Experiencia en proyectos de cierre minero
- Implementación de metodologías científicas avanzadas

### Contacto
Para soporte técnico, consultas o mejoras, contactar con el equipo de desarrollo.

### Actualizaciones
Este plugin se actualiza regularmente con:
- Nuevos algoritmos científicos
- Mejoras de rendimiento
- Características adicionales
- Corrección de errores

## Licencia

Este software está licenciado para uso en proyectos de ingeniería y restauración ambiental. Consulte los términos específicos de licencia para uso comercial.

---

**Natural Regrade Plugin v1.0**  
*Transformando paisajes mineros en ecosistemas sostenibles*
