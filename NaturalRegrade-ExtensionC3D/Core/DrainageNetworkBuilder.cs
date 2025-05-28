using System;
using System.Collections.Generic;
using System.Linq;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.Civil.DatabaseServices;

namespace NaturalRegrade_addon.Core
{
    /// <summary>
    /// Constructor de redes de drenaje naturales
    /// Genera líneas de drenaje siguiendo principios geomorfológicos naturales
    /// Basado en patrones de morfología fluvial de Zapico et al. (2018)
    /// </summary>
    public class DrainageNetworkBuilder
    {
        private HydrologicAnalyzer hydrologicData;
        private List<DrainageLine> drainageNetwork;

        /// <summary>
        /// Clase que representa una línea de drenaje individual
        /// </summary>
        public class DrainageLine
        {
            public List<Point3d> Points { get; set; } = new List<Point3d>();
            public double FlowAccumulation { get; set; }
            public int Order { get; set; } // Orden de Strahler
            public Polyline AutoCADPolyline { get; set; }

            /// <summary>
            /// Convierte la línea de drenaje a una polilínea de AutoCAD
            /// </summary>
            public Polyline ToAutoCADPolyline()
            {
                if (Points.Count < 2) return null;

                var polyline = new Polyline();
                for (int i = 0; i < Points.Count; i++)
                {
                    polyline.AddVertexAt(i, new Point2d(Points[i].X, Points[i].Y), 0, 0, 0);
                }

                return polyline;
            }
        }

        /// <summary>
        /// Inicializa el constructor con datos hidrológicos
        /// </summary>
        /// <param name="analyzer">Analizador hidrológico con datos calculados</param>
        public void Initialize(HydrologicAnalyzer analyzer)
        {
            hydrologicData = analyzer ?? throw new ArgumentNullException(nameof(analyzer));
            drainageNetwork = new List<DrainageLine>();
        }

        /// <summary>
        /// Genera la red de drenaje completa
        /// </summary>
        /// <param name="minAccumulation">Acumulación mínima para considerar un curso de agua</param>
        /// <param name="smoothingFactor">Factor de suavizado de las líneas (0-1)</param>
        /// <returns>Lista de líneas de drenaje generadas</returns>
        public List<DrainageLine> GenerateDrainageNetwork(double minAccumulation = 100, 
                                                          double smoothingFactor = 0.3)
        {
            try
            {
                // 1. Identificar puntos de alta acumulación
                var drainagePoints = hydrologicData.IdentifyDrainagePoints(minAccumulation);

                // 2. Generar líneas de drenaje principales
                var processedPoints = new HashSet<(int, int)>();
                
                foreach (var point in drainagePoints)
                {
                    if (processedPoints.Contains((point.row, point.col)))
                        continue;

                    var drainageLine = TraceDrainagePath(point.row, point.col, processedPoints);
                    if (drainageLine != null && drainageLine.Points.Count > 3)
                    {
                        // Aplicar suavizado geomorfológico
                        SmoothDrainageLine(drainageLine, smoothingFactor);
                        
                        // Calcular orden de Strahler
                        drainageLine.Order = CalculateStreamOrder(drainageLine);
                        
                        drainageNetwork.Add(drainageLine);
                    }
                }

                // 3. Optimizar la red conectando confluencias
                OptimizeDrainageNetwork();

                // 4. Aplicar principios de morfología fluvial natural
                ApplyNaturalMorphology();

                return drainageNetwork;
            }
            catch (Exception ex)
            {
                throw new Exception($"Error generando red de drenaje: {ex.Message}");
            }
        }

        /// <summary>
        /// Traza una línea de drenaje desde un punto dado
        /// </summary>
        private DrainageLine TraceDrainagePath(int startRow, int startCol, 
                                             HashSet<(int, int)> processedPoints)
        {
            var drainageLine = new DrainageLine();
            var pathPoints = hydrologicData.TraceDrainageLine(startRow, startCol);

            if (pathPoints.Count < 2) return null;

            // Convertir coordenadas de malla a coordenadas del mundo
            foreach (var (row, col) in pathPoints)
            {
                processedPoints.Add((row, col));
                
                // Calcular coordenadas del mundo
                double x = col * hydrologicData.CellSize;
                double y = (hydrologicData.Rows - row - 1) * hydrologicData.CellSize;
                double z = hydrologicData.ElevationGrid[row, col];

                if (!double.IsNaN(z))
                {
                    drainageLine.Points.Add(new Point3d(x, y, z));
                }
            }

            // Establecer acumulación de flujo
            if (pathPoints.Count > 0)
            {
                var (row, col) = pathPoints[0];
                drainageLine.FlowAccumulation = hydrologicData.FlowAccumulation[row, col];
            }

            return drainageLine;
        }

        /// <summary>
        /// Aplica suavizado geomorfológico a una línea de drenaje
        /// Basado en filtros Laplacianos adaptados para morfología fluvial
        /// </summary>
        private void SmoothDrainageLine(DrainageLine drainageLine, double smoothingFactor)
        {
            if (drainageLine.Points.Count < 4) return;

            var smoothedPoints = new List<Point3d>();
            smoothedPoints.Add(drainageLine.Points[0]); // Mantener primer punto

            // Aplicar suavizado Laplaciano modificado
            for (int i = 1; i < drainageLine.Points.Count - 1; i++)
            {
                var prevPoint = drainageLine.Points[i - 1];
                var currentPoint = drainageLine.Points[i];
                var nextPoint = drainageLine.Points[i + 1];

                // Calcular punto suavizado usando promedio ponderado
                double newX = currentPoint.X + smoothingFactor * 
                             ((prevPoint.X + nextPoint.X) / 2.0 - currentPoint.X);
                double newY = currentPoint.Y + smoothingFactor * 
                             ((prevPoint.Y + nextPoint.Y) / 2.0 - currentPoint.Y);
                
                // Mantener la tendencia de elevación natural
                double newZ = (prevPoint.Z + currentPoint.Z + nextPoint.Z) / 3.0;

                smoothedPoints.Add(new Point3d(newX, newY, newZ));
            }

            smoothedPoints.Add(drainageLine.Points.Last()); // Mantener último punto
            drainageLine.Points = smoothedPoints;
        }

        /// <summary>
        /// Calcula el orden de Strahler para una línea de drenaje
        /// </summary>
        private int CalculateStreamOrder(DrainageLine drainageLine)
        {
            // Implementación simplificada basada en acumulación de flujo
            if (drainageLine.FlowAccumulation > 10000) return 4;
            if (drainageLine.FlowAccumulation > 1000) return 3;
            if (drainageLine.FlowAccumulation > 100) return 2;
            return 1;
        }

        /// <summary>
        /// Optimiza la red de drenaje conectando confluencias
        /// </summary>
        private void OptimizeDrainageNetwork()
        {
            // Identificar confluencias y optimizar conexiones
            const double confluenceThreshold = 50.0; // metros

            for (int i = 0; i < drainageNetwork.Count; i++)
            {
                for (int j = i + 1; j < drainageNetwork.Count; j++)
                {
                    ConnectIfConfluent(drainageNetwork[i], drainageNetwork[j], confluenceThreshold);
                }
            }
        }

        /// <summary>
        /// Conecta dos líneas de drenaje si están suficientemente cerca
        /// </summary>
        private void ConnectIfConfluent(DrainageLine line1, DrainageLine line2, double threshold)
        {
            if (line1.Points.Count == 0 || line2.Points.Count == 0) return;

            var endPoint1 = line1.Points.Last();
            var endPoint2 = line2.Points.Last();
            var startPoint1 = line1.Points.First();
            var startPoint2 = line2.Points.First();

            // Verificar si el final de una línea está cerca del inicio de otra
            if (endPoint1.DistanceTo(startPoint2) < threshold)
            {
                // Conectar line1 final con line2 inicio
                line1.Points.AddRange(line2.Points.Skip(1));
                drainageNetwork.Remove(line2);
            }
            else if (endPoint2.DistanceTo(startPoint1) < threshold)
            {
                // Conectar line2 final con line1 inicio
                line2.Points.AddRange(line1.Points.Skip(1));
                drainageNetwork.Remove(line1);
            }
        }

        /// <summary>
        /// Aplica principios de morfología fluvial natural
        /// Basado en patrones de meandering y sinuosidad natural
        /// </summary>
        private void ApplyNaturalMorphology()
        {
            foreach (var drainageLine in drainageNetwork)
            {
                ApplyNaturalSinuosity(drainageLine);
                AdjustBankfullWidth(drainageLine);
            }
        }

        /// <summary>
        /// Aplica sinuosidad natural a las líneas de drenaje
        /// </summary>
        private void ApplyNaturalSinuosity(DrainageLine drainageLine)
        {
            if (drainageLine.Points.Count < 4) return;

            // Calcular sinuosidad objetivo basada en el orden del stream
            double targetSinuosity = 1.2 + (drainageLine.Order - 1) * 0.1;
            
            // Aplicar pequeñas desviaciones para crear meandering natural
            var random = new Random(drainageLine.GetHashCode());
            
            for (int i = 1; i < drainageLine.Points.Count - 1; i++)
            {
                if (i % 3 == 0) // Aplicar cada 3 puntos para evitar sobre-procesamiento
                {
                    var point = drainageLine.Points[i];
                    double deviation = (random.NextDouble() - 0.5) * 2.0 * 
                                     drainageLine.Order; // Mayor desviación para streams de orden superior
                    
                    var newPoint = new Point3d(
                        point.X + deviation,
                        point.Y + deviation * 0.5,
                        point.Z
                    );
                    
                    drainageLine.Points[i] = newPoint;
                }
            }
        }

        /// <summary>
        /// Ajusta el ancho de bankfull basado en el orden del stream
        /// </summary>
        private void AdjustBankfullWidth(DrainageLine drainageLine)
        {
            // Implementación para futuras mejoras de visualización
            // El ancho puede usarse para generar corredores de inundación
            double bankfullWidth = Math.Pow(2, drainageLine.Order) * 2.0; // metros
            // Esta información puede usarse posteriormente para modelado 3D
        }

        /// <summary>
        /// Crea las polilíneas de AutoCAD para la red de drenaje
        /// </summary>
        /// <param name="database">Base de datos de AutoCAD</param>
        /// <param name="layerName">Nombre de la capa donde crear las líneas</param>
        public void CreateAutoCADPolylines(Database database, string layerName = "DRAINAGE_NETWORK")
        {
            using (var transaction = database.TransactionManager.StartTransaction())
            {
                try
                {
                    var blockTable = transaction.GetObject(database.BlockTableId, OpenMode.ForRead) as BlockTable;
                    var modelSpace = transaction.GetObject(blockTable[BlockTableRecord.ModelSpace], 
                                                         OpenMode.ForWrite) as BlockTableRecord;

                    // Crear capa si no existe
                    CreateLayerIfNotExists(database, transaction, layerName);

                    foreach (var drainageLine in drainageNetwork)
                    {
                        var polyline = drainageLine.ToAutoCADPolyline();
                        if (polyline != null)
                        {
                            polyline.Layer = layerName;
                            
                            // Asignar color basado en el orden del stream
                            polyline.ColorIndex = GetColorByOrder(drainageLine.Order);
                            
                            modelSpace.AppendEntity(polyline);
                            transaction.AddNewlyCreatedDBObject(polyline, true);
                            
                            drainageLine.AutoCADPolyline = polyline;
                        }
                    }

                    transaction.Commit();
                }
                catch
                {
                    transaction.Abort();
                    throw;
                }
            }
        }

        /// <summary>
        /// Crea una capa si no existe
        /// </summary>
        private void CreateLayerIfNotExists(Database database, Transaction transaction, string layerName)
        {
            var layerTable = transaction.GetObject(database.LayerTableId, OpenMode.ForRead) as LayerTable;
            
            if (!layerTable.Has(layerName))
            {
                layerTable.UpgradeOpen();
                var layer = new LayerTableRecord
                {
                    Name = layerName,
                    Color = Autodesk.AutoCAD.Colors.Color.FromColorIndex(
                        Autodesk.AutoCAD.Colors.ColorMethod.ByAci, 4) // Cyan
                };
                
                layerTable.Add(layer);
                transaction.AddNewlyCreatedDBObject(layer, true);
            }
        }

        /// <summary>
        /// Obtiene color basado en el orden del stream
        /// </summary>
        private short GetColorByOrder(int order)
        {
            switch (order)
            {
                case 1: return 4; // Cyan - streams pequeños
                case 2: return 5; // Blue - streams medianos
                case 3: return 6; // Magenta - streams grandes
                case 4: return 1; // Red - ríos principales
                default: return 7; // White
            }
        }

        /// <summary>
        /// Propiedades de acceso
        /// </summary>
        public List<DrainageLine> DrainageNetwork => drainageNetwork;
    }
}
