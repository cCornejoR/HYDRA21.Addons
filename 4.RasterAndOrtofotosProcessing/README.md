# HYDRA21 Orthophoto Processor Pro

Professional orthophoto processing application with geospatial data preservation, built with Flet and modern Python technologies.

## 🌟 Features

### Core Capabilities

- **Advanced Orthophoto Processing**: Process large TIF orthophoto files while preserving georeferenciation data
- **Multiple Export Formats**: Export as JPEG, PNG, or optimized GeoTIFF with georeferenciation preserved
- **Batch Processing**: Process multiple orthophoto files efficiently
- **Geospatial Data Preservation**: Maintain coordinate reference systems and spatial metadata

### User Interface

- **Modern Design**: Professional Flet-based interface with blue color scheme
- **Dark/Light Mode**: Dynamic theme switching with consistent design
- **Progress Indicators**: Comprehensive progress bars, spinners, and statistics
- **Tabbed Interface**: Organized workflow with Files, Options, Processing, and Results tabs
- **No Shadows UI**: Clean, modern interface following user preferences

### Processing Options

- **Compression Methods**: LZW, DEFLATE, JPEG, PACKBITS compression options
- **Quality Control**: Adjustable quality settings for lossy compression
- **Export Profiles**: Pre-configured profiles for different use cases
- **Resampling Methods**: Multiple resampling algorithms for optimal results

### Results & Statistics

- **Detailed Statistics**: File paths, compression ratios, processing time
- **Direct File Access**: Open files and folders directly from results
- **Processing Reports**: Comprehensive processing summaries
- **Error Handling**: Detailed error reporting and recovery options

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- GDAL library installed on your system

### Installation

#### Option 1: Automated Installation (Recommended)

```bash
python install.py
```

#### Option 2: Manual Installation

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main_professional.py
   ```

#### Option 3: Interactive Launcher

```bash
python launch.py
```

#### Option 4: Windows Batch File

Double-click `launch.bat` or run:

```cmd
launch.bat
```

#### Option 5: Legacy Version

```bash
python main.py
```

### First Use

1. **Select Files**: Use the "Archivos" tab to select orthophoto files
2. **Configure Options**: Set processing options in the "Opciones" tab
3. **Process**: Start processing in the "Procesar" tab
4. **View Results**: Check results and access files in the "Resultados" tab

## 📁 Project Structure

```
4.RasterAndOrtofotosProcessing/
├── config/                     # Configuration files
│   ├── settings.py            # Application settings and themes
│   ├── orthophoto_config.py   # Geospatial processing configuration
│   └── __init__.py
├── ui/                        # User interface components
│   ├── themes/
│   │   ├── theme_manager.py   # Theme management system
│   │   └── __init__.py
│   ├── components/
│   │   ├── tabbed_interface.py    # Main tabbed interface
│   │   ├── file_manager.py        # File selection and management
│   │   ├── processing_options.py  # Processing configuration
│   │   ├── progress_display.py    # Progress indicators
│   │   ├── results_panel.py       # Results display
│   │   └── __init__.py
│   └── __init__.py
├── core/                      # Core processing logic
│   ├── orthophoto_engine.py   # Main processing engine
│   └── __init__.py
├── main_professional.py       # Professional application entry point
├── main.py                    # Legacy/redirect entry point
├── launch.py                  # Interactive launcher script
├── install.py                 # Automated installation script
├── test_basic.py              # Basic functionality test
├── launch.bat                 # Windows batch launcher
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Supported Input Formats

- **TIF/TIFF**: GeoTIFF files with georeferenciation
- **ECW**: Enhanced Compression Wavelet files
- **JP2**: JPEG 2000 files
- **IMG**: ERDAS IMAGINE files
- **BIL/BIP/BSQ**: ENVI format files

### Export Options

- **GeoTIFF**: Compressed GeoTIFF with preserved georeferenciation
- **JPEG**: JPEG with world file for georeferenciation
- **PNG**: PNG with world file for georeferenciation

### Compression Presets

- **Lossless**: Maximum quality, larger file size (LZW/DEFLATE)
- **High Quality**: Excellent quality, moderate size (DEFLATE/JPEG 95%)
- **Medium Quality**: Good quality, reduced size (JPEG 85%)
- **Basic Quality**: Acceptable quality, minimum size (JPEG 70%)

## 🎨 Theme System

The application features a professional blue color scheme with support for both light and dark modes:

### Light Theme

- Primary: Blue (#2563eb)
- Secondary: Purple (#7c3aed)
- Accent: Green (#059669)
- Background: Light gray (#f8fafc)

### Dark Theme

- Primary: Light blue (#3b82f6)
- Secondary: Light purple (#8b5cf6)
- Accent: Light green (#10b981)
- Background: Dark slate (#0f172a)

## 🛠️ Technical Details

### Dependencies

- **Flet**: Modern GUI framework based on Flutter
- **Rasterio**: Geospatial raster data processing
- **GDAL**: Geospatial Data Abstraction Library
- **NumPy**: Numerical computing support

### Performance Features

- **Memory Management**: Efficient handling of large orthophoto files
- **Chunked Processing**: Process large files in manageable chunks
- **Progress Tracking**: Real-time progress updates and statistics
- **Error Recovery**: Robust error handling and recovery mechanisms

## 📊 Processing Workflow

1. **File Validation**: Verify file formats and geospatial metadata
2. **Configuration**: Apply user-selected processing options
3. **Processing**: Transform files with progress tracking
4. **Quality Assessment**: Verify output quality and compression ratios
5. **Results**: Display comprehensive statistics and provide file access

## 🔍 Troubleshooting

### Common Issues

**GDAL/Rasterio Installation**:

- Windows: Use conda or OSGeo4W installer
- Linux: Install gdal-dev package
- macOS: Use Homebrew or conda

**Memory Issues**:

- Reduce chunk size in processing configuration
- Close other applications to free memory
- Process files individually for very large files

**File Format Issues**:

- Ensure input files have valid georeferenciation
- Check file permissions and accessibility
- Verify file integrity before processing

## 📝 License

© 2024 HYDRA21 - Orthophoto Processor Pro

## 🤝 Contributing

This is part of the HYDRA21 addon suite. For contributions and issues, please refer to the main HYDRA21 project repository.

## 📞 Support

For technical support and questions, please refer to the HYDRA21 documentation or contact the development team.
