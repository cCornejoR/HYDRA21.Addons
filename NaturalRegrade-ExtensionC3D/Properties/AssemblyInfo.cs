using System.Reflection;
using System.Runtime.InteropServices;
using Autodesk.AutoCAD.Runtime;

// Información general del ensamblado
[assembly: AssemblyTitle("Natural Regrade Extension for Civil 3D")]
[assembly: AssemblyDescription("Plugin de análisis geomorfológico avanzado para Autodesk Civil 3D. Implementa metodología GeoFluv para crear superficies naturales resistentes a erosión en proyectos de cierre minero.")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Hydra21 Solutions")]
[assembly: AssemblyProduct("Natural Regrade Plugin")]
[assembly: AssemblyCopyright("Copyright © Hydra21 Solutions 2025")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]

// Configuración COM
[assembly: ComVisible(false)]

// GUID del ensamblado
[assembly: Guid("12345678-1234-5678-9ABC-123456789ABC")]

// Información de versión
[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]
[assembly: AssemblyInformationalVersion("1.0.0-beta")]

// Configuración específica de AutoCAD
[assembly: ExtensionApplication(typeof(NaturalRegrade_addon.PluginEntryPoint))]

// Configuración de comandos
[assembly: CommandClass(typeof(NaturalRegrade_addon.PluginEntryPoint))]
