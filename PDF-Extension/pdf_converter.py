# pdf_converter.py
"""
Módulo para la conversión de archivos PDF a otros formatos.

Este módulo proporciona funciones para convertir archivos PDF a formatos de imagen
(JPEG, PNG, TIFF) y a formato DOCX utilizando Ghostscript.
"""

import subprocess
import os
from pathlib import Path
from typing import Union, Optional

# Asumiendo que GhostscriptUtils podría ser útil aquí, o se implementarán funciones directas.
# from .utils import GhostscriptUtils # Descomentar si se usa GhostscriptUtils

class PDFConversionError(Exception):
    """Excepción personalizada para errores durante la conversión de PDF."""
    pass

class PDFConverter:
    """Clase para manejar la conversión de archivos PDF."""

    def __init__(self, gs_path: str = "gswin64c"):
        """
        Inicializa el convertidor de PDF.

        Args:
            gs_path (str): Ruta al ejecutable de Ghostscript.
                           Por defecto es 'gswin64c' para Windows.
        """
        self.gs_path = gs_path
        # self.gs_utils = GhostscriptUtils(gs_path=gs_path) # Descomentar si se usa GhostscriptUtils

    def _run_gs_command(self, command: list[str]) -> None:
        """
        Ejecuta un comando de Ghostscript y maneja errores.

        Args:
            command (list[str]): Lista de argumentos para el comando de Ghostscript.

        Raises:
            PDFConversionError: Si Ghostscript retorna un código de error.
        """
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                error_message = f"Error de Ghostscript (código {process.returncode}):\n{stderr}"
                if stdout:
                    error_message += f"\nSalida estándar:\n{stdout}"
                raise PDFConversionError(error_message)
            print(f"Comando Ghostscript ejecutado con éxito. Salida:\n{stdout}")
        except FileNotFoundError:
            raise PDFConversionError(f"No se encontró el ejecutable de Ghostscript en '{self.gs_path}'. Asegúrate de que esté instalado y en el PATH, o proporciona la ruta correcta.")
        except Exception as e:
            raise PDFConversionError(f"Ocurrió un error inesperado al ejecutar Ghostscript: {e}")

    def convert_pdf_to_image(
        self,
        pdf_path: Union[str, Path],
        output_dir: Union[str, Path],
        image_format: str = "png",
        resolution: int = 300,
        prefix: str = "page"
    ) -> list[Path]:
        """
        Convierte las páginas de un archivo PDF a imágenes.

        Args:
            pdf_path (Union[str, Path]): Ruta al archivo PDF de entrada.
            output_dir (Union[str, Path]): Directorio donde se guardarán las imágenes.
            image_format (str): Formato de imagen de salida ('jpeg', 'png', 'tiff').
                                Por defecto es 'png'.
            resolution (int): Resolución de las imágenes en DPI. Por defecto es 300.
            prefix (str): Prefijo para los nombres de archivo de las imágenes generadas.
                          Por defecto es 'page'.

        Returns:
            list[Path]: Lista de rutas a las imágenes generadas.

        Raises:
            PDFConversionError: Si ocurre un error durante la conversión.
            ValueError: Si el formato de imagen no es soportado.
        """
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not pdf_path.exists():
            raise PDFConversionError(f"El archivo PDF no existe: {pdf_path}")

        image_format = image_format.lower()
        gs_device_map = {
            "jpeg": "jpeg",
            "png": "png16m",  # Para PNG de 24-bit
            "tiff": "tiff24nc" # Para TIFF de 24-bit sin compresión
        }

        if image_format not in gs_device_map:
            raise ValueError(f"Formato de imagen no soportado: {image_format}. Soportados: jpeg, png, tiff")

        gs_device = gs_device_map[image_format]
        output_filename_pattern = output_dir / f"{prefix}_%04d.{image_format}"

        command = [
            self.gs_path,
            "-dNOPAUSE",
            "-dBATCH",
            "-sDEVICE=" + gs_device,
            f"-r{resolution}",
            f"-sOutputFile={str(output_filename_pattern)}",
            str(pdf_path)
        ]

        print(f"Ejecutando comando para convertir PDF a {image_format.upper()}: {' '.join(command)}")
        self._run_gs_command(command)

        # Encontrar los archivos generados
        generated_files = sorted(list(output_dir.glob(f"{prefix}_*.{image_format}")))
        if not generated_files:
            raise PDFConversionError(f"No se generaron imágenes. Verifica la salida de Ghostscript.")
        
        print(f"Imágenes generadas: {generated_files}")
        return generated_files

    def convert_pdf_to_docx(
        self,
        pdf_path: Union[str, Path],
        output_path: Union[str, Path]
    ) -> Path:
        """
        Convierte un archivo PDF a formato DOCX.
        Nota: La calidad de la conversión puede variar y depende de la complejidad del PDF.
              Ghostscript utiliza el dispositivo 'docxwrite'.

        Args:
            pdf_path (Union[str, Path]): Ruta al archivo PDF de entrada.
            output_path (Union[str, Path]): Ruta completa para el archivo DOCX de salida (incluyendo .docx).

        Returns:
            Path: Ruta al archivo DOCX generado.

        Raises:
            PDFConversionError: Si ocurre un error durante la conversión.
        """
        pdf_path = Path(pdf_path)
        output_path = Path(output_path)

        if not pdf_path.exists():
            raise PDFConversionError(f"El archivo PDF no existe: {pdf_path}")
        
        if output_path.suffix.lower() != ".docx":
            # Asegurar que la extensión sea .docx
            output_path = output_path.with_suffix(".docx")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        command = [
            self.gs_path,
            "-dNOPAUSE",
            "-dBATCH",
            "-sDEVICE=docxwrite",
            f"-sOutputFile={str(output_path)}",
            str(pdf_path)
        ]

        print(f"Ejecutando comando para convertir PDF a DOCX: {' '.join(command)}")
        self._run_gs_command(command)

        if not output_path.exists():
            raise PDFConversionError(f"No se generó el archivo DOCX. Verifica la salida de Ghostscript.")
        
        print(f"Archivo DOCX generado: {output_path}")
        return output_path

    def convert_pdf_page_to_docx(
        self,
        pdf_path: Union[str, Path],
        page_number: int,
        output_docx_path: Union[str, Path],
        temp_dir: Union[str, Path]
    ) -> Path:
        """
        Extrae una página específica de un PDF y la convierte a DOCX.

        Args:
            pdf_path (Union[str, Path]): Ruta al archivo PDF de entrada.
            page_number (int): Número de la página a extraer (1-indexado).
            output_docx_path (Union[str, Path]): Ruta completa para el archivo DOCX de salida.
            temp_dir (Union[str, Path]): Directorio temporal para archivos intermedios.

        Returns:
            Path: Ruta al archivo DOCX generado.

        Raises:
            PDFConversionError: Si ocurre un error durante la extracción o conversión.
        """
        pdf_path = Path(pdf_path)
        output_docx_path = Path(output_docx_path)
        temp_dir = Path(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        if not pdf_path.exists():
            raise PDFConversionError(f"El archivo PDF no existe: {pdf_path}")

        # 1. Extraer la página específica a un PDF temporal
        temp_pdf_path = temp_dir / f"temp_page_{page_number}_{pdf_path.stem}.pdf"
        
        command = [
            self.gs_path,
            "-dNOPAUSE",
            "-dBATCH",
            f"-dFirstPage={page_number}",
            f"-dLastPage={page_number}",
            "-sDEVICE=pdfwrite",
            f"-sOutputFile={str(temp_pdf_path)}",
            str(pdf_path)
        ]

        print(f"Ejecutando comando para extraer página {page_number} a PDF temporal: {' '.join(command)}")
        self._run_gs_command(command)

        if not temp_pdf_path.exists():
            raise PDFConversionError(f"No se pudo extraer la página {page_number} a PDF temporal.")

        # 2. Convertir el PDF temporal de una sola página a DOCX
        try:
            generated_docx_path = self.convert_pdf_to_docx(temp_pdf_path, output_docx_path)
        finally:
            # Limpiar el archivo PDF temporal
            if temp_pdf_path.exists():
                os.remove(temp_pdf_path)
                print(f"Archivo temporal eliminado: {temp_pdf_path}")

        return generated_docx_path

    def render_pdf_page_to_image(
        self,
        pdf_path: Union[str, Path],
        page_number: int,
        output_image_path: Union[str, Path],
        image_format: str = "png",
        resolution: int = 150
    ) -> Path:
        """
        Renderiza una página específica de un archivo PDF a una imagen.

        Args:
            pdf_path (Union[str, Path]): Ruta al archivo PDF de entrada.
            page_number (int): Número de la página a renderizar (1-indexado).
            output_image_path (Union[str, Path]): Ruta completa para la imagen de salida.
            image_format (str): Formato de imagen de salida ('jpeg', 'png', 'tiff').
                                Por defecto es 'png'.
            resolution (int): Resolución de la imagen en DPI. Por defecto es 150.

        Returns:
            Path: Ruta a la imagen generada.

        Raises:
            PDFConversionError: Si ocurre un error durante la renderización.
            ValueError: Si el formato de imagen no es soportado o el número de página es inválido.
        """
        pdf_path = Path(pdf_path)
        output_image_path = Path(output_image_path)

        if not pdf_path.exists():
            raise PDFConversionError(f"El archivo PDF no existe: {pdf_path}")
        
        if page_number <= 0:
            raise ValueError("El número de página debe ser mayor que 0.")

        output_image_path.parent.mkdir(parents=True, exist_ok=True)

        image_format = image_format.lower()
        gs_device_map = {
            "jpeg": "jpeg",
            "png": "png16m",
            "tiff": "tiff24nc"
        }

        if image_format not in gs_device_map:
            raise ValueError(f"Formato de imagen no soportado: {image_format}. Soportados: jpeg, png, tiff")

        gs_device = gs_device_map[image_format]

        command = [
            self.gs_path,
            "-dNOPAUSE",
            "-dBATCH",
            f"-dFirstPage={page_number}",
            f"-dLastPage={page_number}",
            "-sDEVICE=" + gs_device,
            f"-r{resolution}",
            f"-sOutputFile={str(output_image_path)}",
            str(pdf_path)
        ]

        print(f"Ejecutando comando para renderizar página {page_number} de PDF a {image_format.upper()}: {' '.join(command)}")
        self._run_gs_command(command)

        if not output_image_path.exists():
            raise PDFConversionError(f"No se generó la imagen de la página. Verifica la salida de Ghostscript.")
        
        print(f"Imagen de la página generada: {output_image_path}")
        return output_image_path

    def convert_pdf_page_to_docx(
        self,
        pdf_path: Union[str, Path],
        page_number: int,
        output_docx_path: Union[str, Path],
        temp_dir: Optional[Union[str, Path]] = None
    ) -> Path:
        """
        Converts a specific page from a PDF file to DOCX format.

        Args:
            pdf_path (Union[str, Path]): Path to the input PDF file.
            page_number (int): Page number to convert (1-indexed).
            output_docx_path (Union[str, Path]): Full path for the output DOCX file.
            temp_dir (Optional[Union[str, Path]]): Temporary directory for single-page PDF.
                                                  If None, creates 'temp_pdf_page' in the original PDF directory.

        Returns:
            Path: Path to the generated DOCX file.

        Raises:
            PDFConversionError: If an error occurs during conversion.
            ValueError: If page number is invalid.
        """
        # Convert input paths to Path objects
        pdf_path = Path(pdf_path)
        output_docx_path = Path(output_docx_path)

        # Validate PDF exists
        if not pdf_path.exists():
            raise PDFConversionError(f"El archivo PDF no existe: {pdf_path}")

        # Validate page number
        if page_number <= 0:
            raise ValueError("Page number must be greater than 0")

        # Setup temporary directory
        if temp_dir:
            temp_pdf_dir = Path(temp_dir)
        else:
            temp_pdf_dir = pdf_path.parent / "temp_pdf_page"
        temp_pdf_dir.mkdir(parents=True, exist_ok=True)

        # Create temporary PDF filename
        temp_pdf_filename = f"{pdf_path.stem}_page_{page_number}.pdf"
        temp_single_page_pdf_path = temp_pdf_dir / temp_pdf_filename
        # 1. Extraer la página específica a un nuevo PDF
        extract_command = [
            self.gs_path,
            "-dNOPAUSE",
            "-dBATCH",
            "-sDEVICE=pdfwrite",
            f"-dFirstPage={page_number}",
            f"-dLastPage={page_number}",
            f"-sOutputFile={str(temp_single_page_pdf_path)}",
            str(pdf_path)
        ]
        print(f"Extrayendo página {page_number} a PDF temporal: {' '.join(extract_command)}")
        try:
            self._run_gs_command(extract_command)
            if not temp_single_page_pdf_path.exists():
                raise PDFConversionError(f"No se pudo extraer la página {page_number} a un PDF temporal.")
        except Exception as e:
            # Limpiar PDF temporal si la extracción falla
            if temp_single_page_pdf_path.exists():
                temp_single_page_pdf_path.unlink()
            raise PDFConversionError(f"Error al extraer la página {page_number}: {e}")

        # 2. Convertir el PDF temporal de una página a DOCX
        try:
            generated_docx_path = self.convert_pdf_to_docx(
                pdf_path=temp_single_page_pdf_path,
                output_path=output_docx_path
            )
        finally:
            # 3. Limpiar el PDF temporal
            if temp_single_page_pdf_path.exists():
                try:
                    temp_single_page_pdf_path.unlink()
                    print(f"PDF temporal eliminado: {temp_single_page_pdf_path}")
                except OSError as oe:
                    print(f"Advertencia: No se pudo eliminar el PDF temporal {temp_single_page_pdf_path}: {oe}")
        
        return generated_docx_path

# Ejemplo de uso (para pruebas directas del módulo):
if __name__ == "__main__":
    converter = PDFConverter() # Asume gswin64c en el PATH

    # Crear un PDF de prueba si no existe (requiere reportlab)
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch

        test_pdf_file = Path("test_document.pdf")
        if not test_pdf_file.exists():
            c = canvas.Canvas(str(test_pdf_file), pagesize=letter)
            c.drawString(1 * inch, 10 * inch, "Página 1: Hola Mundo PDF!")
            c.showPage()
            c.drawString(1 * inch, 10 * inch, "Página 2: Contenido de prueba.")
            c.setFillColorRGB(0.8, 0.2, 0.2) # Color rojo
            c.rect(2*inch, 5*inch, 3*inch, 2*inch, fill=1, stroke=0)
            c.showPage()
            c.save()
            print(f"PDF de prueba creado: {test_pdf_file.resolve()}")
        else:
            print(f"Usando PDF de prueba existente: {test_pdf_file.resolve()}")

        output_image_dir = Path("output_images")
        output_docx_dir = Path("output_docx")

        # Test PDF to PNG
        try:
            print("\nConvirtiendo PDF a PNG...")
            png_files = converter.convert_pdf_to_image(test_pdf_file, output_image_dir, image_format="png", resolution=150)
            print(f"PNGs generados: {png_files}")
            if png_files:
                print(f"Verifica las imágenes en: {output_image_dir.resolve()}")
        except PDFConversionError as e:
            print(f"Error al convertir a PNG: {e}")

        # Test PDF to JPEG
        try:
            print("\nConvirtiendo PDF a JPEG...")
            jpeg_files = converter.convert_pdf_to_image(test_pdf_file, output_image_dir, image_format="jpeg", resolution=150)
            print(f"JPEGs generados: {jpeg_files}")
            if jpeg_files:
                 print(f"Verifica las imágenes en: {output_image_dir.resolve()}")
        except PDFConversionError as e:
            print(f"Error al convertir a JPEG: {e}")

        # Test PDF to DOCX
        docx_output_file = output_docx_dir / "converted_document.docx"
        try:
            print("\nConvirtiendo PDF a DOCX...")
            docx_file = converter.convert_pdf_to_docx(test_pdf_file, docx_output_file)
            print(f"DOCX generado: {docx_file}")
            if docx_file.exists():
                print(f"Verifica el DOCX en: {docx_file.resolve()}")
        except PDFConversionError as e:
            print(f"Error al convertir a DOCX: {e}")

    except ImportError:
        print("Para ejecutar las pruebas, instala reportlab: pip install reportlab")
    except PDFConversionError as e:
        print(f"Error general en las pruebas: {e}")
    except Exception as e:
        print(f"Error inesperado en el script de prueba: {e}")