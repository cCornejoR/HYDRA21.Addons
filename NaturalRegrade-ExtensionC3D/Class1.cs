using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Runtime;
using Autodesk.Civil.ApplicationServices;
using Autodesk.Civil.DatabaseServices;
using NaturalRegrade_addon.Core;
using NaturalRegrade_addon.UI;

namespace NaturalRegrade_addon
{
    /// <summary>
    /// Punto de entrada principal del plugin Natural Regrade para Civil 3D
    /// Basado en principios geomorfológicos de GeoFluv para crear superficies naturales
    /// resistentes a la erosión en proyectos de cierre minero
    /// </summary>
    public class PluginEntryPoint : IExtensionApplication
    {        public void Initialize()
        {
            // Inicialización del plugin
            Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc != null)
            {
                doc.Editor.WriteMessage("\nNatural Regrade Plugin v1.0 - Hydra21 Solutions");
                doc.Editor.WriteMessage("\nBasado en tecnología GeoFluv para diseño geomorfológico natural");
                doc.Editor.WriteMessage("\nComando disponible: NATURALREGRADE");
            }
        }

        public void Terminate()
        {
            // Limpieza al cerrar
        }

        /// <summary>
        /// Comando principal NATURALREGRADE
        /// Ejecuta el proceso completo de análisis hidrológico y regrade geomorfológico
        /// </summary>
        [CommandMethod("NATURALREGRADE")]
        public static void ExecuteNaturalRegrade()
        {
            try
            {
                // Obtener documento activo
                Document doc = Application.DocumentManager.MdiActiveDocument;
                if (doc == null)
                {
                    throw new System.Exception("No hay documento activo de Civil 3D");
                }

                Editor ed = doc.Editor;
                ed.WriteMessage("\n=== NATURAL REGRADE - Análisis Geomorfológico ===");

                // Mostrar interfaz de usuario principal
                var mainWindow = new NaturalRegradeMainWindow();
                var result = mainWindow.ShowDialog();

                if (result == true && mainWindow.SelectedSurface != null)
                {
                    // Ejecutar el procesamiento con los parámetros seleccionados
                    var processor = new GeomorphicRegradeProcessor();
                    processor.ProcessSurface(
                        mainWindow.SelectedSurface,
                        mainWindow.ProcessingParameters
                    );
                }
            }
            catch (System.Exception ex)
            {
                Application.DocumentManager.MdiActiveDocument?.Editor
                    .WriteMessage($"\nError en Natural Regrade: {ex.Message}");
            }
        }

        /// <summary>
        /// Comando de información del plugin
        /// </summary>
        [CommandMethod("NATURALREGRADE_INFO")]
        public static void ShowPluginInfo()
        {
            var doc = Application.DocumentManager.MdiActiveDocument;
            if (doc == null) return;

            var ed = doc.Editor;
            ed.WriteMessage("\n╔══════════════════════════════════════════════════╗");
            ed.WriteMessage("\n║           NATURAL REGRADE PLUGIN v1.0           ║");
            ed.WriteMessage("\n║              Hydra21 Solutions                   ║");
            ed.WriteMessage("\n╠══════════════════════════════════════════════════╣");
            ed.WriteMessage("\n║ Funcionalidad:                                   ║");
            ed.WriteMessage("\n║ • Análisis hidrológico de superficies TIN       ║");
            ed.WriteMessage("\n║ • Generación de redes de drenaje naturales      ║");
            ed.WriteMessage("\n║ • Suavizado geomorfológico avanzado             ║");
            ed.WriteMessage("\n║ • Diseño resistente a erosión                   ║");
            ed.WriteMessage("\n║                                                  ║");
            ed.WriteMessage("\n║ Basado en investigación científica:             ║");
            ed.WriteMessage("\n║ • Bugosh & Eckels (2025) - GeoFluv Inc.        ║");
            ed.WriteMessage("\n║ • Hancock et al. (2018) - Env. Modelling       ║");
            ed.WriteMessage("\n║ • Zapico et al. (2018) - Ecological Eng.       ║");
            ed.WriteMessage("\n║                                                  ║");
            ed.WriteMessage("\n║ Comandos disponibles:                           ║");
            ed.WriteMessage("\n║ • NATURALREGRADE - Ejecutar análisis            ║");
            ed.WriteMessage("\n║ • NATURALREGRADE_INFO - Esta información        ║");
            ed.WriteMessage("\n╚══════════════════════════════════════════════════╝");
        }
    }
}
