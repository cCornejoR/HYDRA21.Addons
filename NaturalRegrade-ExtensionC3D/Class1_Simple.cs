using System;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Runtime;

namespace NaturalRegrade_addon
{
    /// <summary>
    /// Simple version of the Natural Regrade plugin for Civil 3D
    /// </summary>
    public class SimplePluginEntryPoint : IExtensionApplication
    {
        public void Initialize()
        {
            // Initialization
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
            // Cleanup
        }

        /// <summary>
        /// Simple NATURALREGRADE command
        /// </summary>
        [CommandMethod("NATURALREGRADE")]
        public static void ExecuteNaturalRegrade()
        {
            try
            {
                Document doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
                if (doc == null)
                {
                    throw new System.Exception("No hay documento activo de Civil 3D");
                }

                Editor ed = doc.Editor;
                ed.WriteMessage("\n=== NATURAL REGRADE - Análisis Geomorfológico ===");
                ed.WriteMessage("\nPlugin cargado correctamente!");
                ed.WriteMessage("\nFuncionalidad completa en desarrollo...");

            }
            catch (System.Exception ex)
            {
                Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument?.Editor
                    .WriteMessage($"\nError en Natural Regrade: {ex.Message}");
            }
        }

        /// <summary>
        /// Plugin info command
        /// </summary>
        [CommandMethod("NATURALREGRADE_INFO")]
        public static void ShowPluginInfo()
        {
            var doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
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
            ed.WriteMessage("\n║ Comandos disponibles:                           ║");
            ed.WriteMessage("\n║ • NATURALREGRADE - Ejecutar análisis            ║");
            ed.WriteMessage("\n║ • NATURALREGRADE_INFO - Esta información        ║");
            ed.WriteMessage("\n╚══════════════════════════════════════════════════╝");
        }
    }
}
