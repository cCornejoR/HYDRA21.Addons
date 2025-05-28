using System;
using System.Collections.Generic;
using System.Linq;
using Autodesk.Civil.DatabaseServices;
using MathNet.Numerics.LinearAlgebra;

namespace NaturalRegrade_addon.Core
{
    /// <summary>
    /// Analizador hidrológico para calcular direcciones de flujo y acumulación
    /// Implementa algoritmos D8 y análisis de cuencas de drenaje
    /// Basado en principios de Bugosh & Eckels (2025) y Hancock et al. (2018)
    /// </summary>
    public class HydrologicAnalyzer
    {
        private double[,] elevationGrid;
        private int rows, cols;
        private double cellSize;
        private FlowDirection[,] flowDirections;
        private double[,] flowAccumulation;

        /// <summary>
        /// Direcciones de flujo D8 (8 direcciones cardinales)
        /// </summary>
        public enum FlowDirection
        {
            None = 0,
            East = 1,
            SouthEast = 2,
            South = 4,
            SouthWest = 8,
            West = 16,
            NorthWest = 32,
            North = 64,
            NorthEast = 128
        }

        /// <summary>
        /// Inicializa el analizador con una superficie TIN
        /// </summary>
        /// <param name="tinSurface">Superficie TIN de Civil 3D</param>
        /// <param name="gridResolution">Resolución de la malla en metros</param>
        public void Initialize(TinSurface tinSurface, double gridResolution = 5.0)
        {
            cellSize = gridResolution;
            ConvertTinToGrid(tinSurface);
            CalculateFlowDirections();
            CalculateFlowAccumulation();
        }

        /// <summary>
        /// Convierte una superficie TIN a una malla de elevaciones regular
        /// </summary>
        private void ConvertTinToGrid(TinSurface tinSurface)
        {            try
            {
                // Obtener límites de la superficie usando Civil 3D API
                double minX, maxX, minY, maxY;                try
                {
                    // Implementar obtención de límites reales de superficie TIN usando Civil 3D API
                    
                    // Método 1: Intentar usar Statistics de la superficie
                    var stats = tinSurface.GetGeneralProperties();
                    if (stats != null)
                    {
                        // Acceder a los límites usando las propiedades de estadísticas
                        minX = stats.MinimumEastingCoordinate;
                        maxX = stats.MaximumEastingCoordinate;
                        minY = stats.MinimumNorthingCoordinate;
                        maxY = stats.MaximumNorthingCoordinate;
                        
                        System.Diagnostics.Debug.WriteLine($"Límites superficie obtenidos: X[{minX:F2}, {maxX:F2}], Y[{minY:F2}, {maxY:F2}]");
                    }
                    else
                    {
                        // Método 2: Calcular límites iterando sobre vértices de la superficie
                        var vertices = tinSurface.GetVertices();
                        if (vertices != null && vertices.Count > 0)
                        {
                            minX = maxX = vertices[0].Location.X;
                            minY = maxY = vertices[0].Location.Y;
                            
                            foreach (var vertex in vertices)
                            {
                                var pt = vertex.Location;
                                if (pt.X < minX) minX = pt.X;
                                if (pt.X > maxX) maxX = pt.X;
                                if (pt.Y < minY) minY = pt.Y;
                                if (pt.Y > maxY) maxY = pt.Y;
                            }
                            
                            System.Diagnostics.Debug.WriteLine($"Límites calculados desde vértices: X[{minX:F2}, {maxX:F2}], Y[{minY:F2}, {maxY:F2}]");
                        }
                        else
                        {
                            // Fallback: usar límites predeterminados con warning
                            minX = 0; maxX = 1000;
                            minY = 0; maxY = 1000;
                            System.Diagnostics.Debug.WriteLine("ADVERTENCIA: No se pudieron obtener límites de superficie, usando valores por defecto");
                        }
                    }
                }
                catch
                {
                    // Fallback: usar límites predeterminados
                    minX = 0; maxX = 1000;
                    minY = 0; maxY = 1000;
                }

                // Calcular dimensiones de la malla
                cols = (int)Math.Ceiling((maxX - minX) / cellSize);
                rows = (int)Math.Ceiling((maxY - minY) / cellSize);

                elevationGrid = new double[rows, cols];
                flowDirections = new FlowDirection[rows, cols];
                flowAccumulation = new double[rows, cols];

                // Interpolar elevaciones en la malla
                for (int i = 0; i < rows; i++)
                {
                    for (int j = 0; j < cols; j++)
                    {
                        double x = minX + j * cellSize + cellSize / 2;
                        double y = maxY - i * cellSize - cellSize / 2; // Y invertido

                        try
                        {
                            // Obtener elevación interpolada de la superficie TIN
                            var point = new Autodesk.AutoCAD.Geometry.Point3d(x, y, 0);
                            double elevation = tinSurface.FindElevationAtXY(x, y);
                            elevationGrid[i, j] = elevation;
                        }
                        catch
                        {
                            // Si no se puede interpolar, usar valor por defecto
                            elevationGrid[i, j] = double.NaN;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                throw new Exception($"Error convirtiendo TIN a malla: {ex.Message}");
            }
        }        /// <summary>
        /// Calcula direcciones de flujo usando algoritmo D8 mejorado
        /// Implementa metodología Bugosh & Eckels (2025) con validación de pendientes
        /// </summary>
        private void CalculateFlowDirections()
        {
            // Direcciones D8: dx, dy para cada dirección con factores de distancia
            int[] dx = { 1, 1, 0, -1, -1, -1, 0, 1 };
            int[] dy = { 0, 1, 1, 1, 0, -1, -1, -1 };
            double[] distances = { 1.0, Math.Sqrt(2), 1.0, Math.Sqrt(2), 1.0, Math.Sqrt(2), 1.0, Math.Sqrt(2) };
            
            FlowDirection[] directions = {
                FlowDirection.East, FlowDirection.SouthEast, FlowDirection.South,
                FlowDirection.SouthWest, FlowDirection.West, FlowDirection.NorthWest,
                FlowDirection.North, FlowDirection.NorthEast
            };

            int processedCells = 0;
            int errorCells = 0;

            for (int i = 1; i < rows - 1; i++)
            {
                for (int j = 1; j < cols - 1; j++)
                {
                    try
                    {
                        if (double.IsNaN(elevationGrid[i, j]))
                        {
                            flowDirections[i, j] = FlowDirection.None;
                            errorCells++;
                            continue;
                        }

                        double currentElevation = elevationGrid[i, j];
                        double maxSlope = 0;
                        FlowDirection steepestDirection = FlowDirection.None;

                        // Analizar las 8 direcciones vecinas
                        for (int k = 0; k < 8; k++)
                        {
                            int ni = i + dy[k];
                            int nj = j + dx[k];

                            if (ni >= 0 && ni < rows && nj >= 0 && nj < cols &&
                                !double.IsNaN(elevationGrid[ni, nj]))
                            {
                                double neighborElevation = elevationGrid[ni, nj];
                                double elevationDrop = currentElevation - neighborElevation;
                                
                                // Calcular pendiente usando distancia real (considerando diagonales)
                                double slope = elevationDrop / (gridResolution * distances[k]);
                                
                                if (slope > maxSlope && slope > 0.001) // Pendiente mínima de 0.1%
                                {
                                    maxSlope = slope;
                                    steepestDirection = directions[k];
                                }
                            }
                        }

                        flowDirections[i, j] = steepestDirection;
                        
                        // Si no hay dirección de flujo clara, aplicar análisis secundario
                        if (steepestDirection == FlowDirection.None)
                        {
                            flowDirections[i, j] = DetermineFlowFromContext(i, j, currentElevation);
                        }
                        
                        processedCells++;
                    }
                    catch (Exception ex)
                    {
                        flowDirections[i, j] = FlowDirection.None;
                        errorCells++;
                        System.Diagnostics.Debug.WriteLine($"Error procesando celda ({i},{j}): {ex.Message}");
                    }
                }
            }
            
            // Log estadísticas del procesamiento
            System.Diagnostics.Debug.WriteLine($"Flow directions calculated: {processedCells} processed, {errorCells} errors");
        }
        
        /// <summary>
        /// Determina dirección de flujo basada en contexto local cuando no hay pendiente clara
        /// </summary>
        private FlowDirection DetermineFlowFromContext(int i, int j, double currentElevation)
        {
            // Analizar elevaciones en una ventana 5x5 para determinar tendencia general
            double sumX = 0, sumY = 0;
            int validNeighbors = 0;
            
            for (int di = -2; di <= 2; di++)
            {
                for (int dj = -2; dj <= 2; dj++)
                {
                    if (di == 0 && dj == 0) continue;
                    
                    int ni = i + di;
                    int nj = j + dj;
                    
                    if (ni >= 0 && ni < rows && nj >= 0 && nj < cols && 
                        !double.IsNaN(elevationGrid[ni, nj]))
                    {
                        double neighborElevation = elevationGrid[ni, nj];
                        double weight = currentElevation - neighborElevation;
                        
                        if (weight > 0) // Solo considerar vecinos más bajos
                        {
                            sumX += dj * weight;
                            sumY += di * weight;
                            validNeighbors++;
                        }
                    }
                }
            }
            
            if (validNeighbors == 0) return FlowDirection.None;
            
            // Determinar dirección principal basada en gradiente promedio
            double avgX = sumX / validNeighbors;
            double avgY = sumY / validNeighbors;
            
            // Convertir a dirección D8 más cercana
            double angle = Math.Atan2(avgY, avgX) * 180.0 / Math.PI;
            if (angle < 0) angle += 360;
            
            int directionIndex = (int)Math.Round(angle / 45.0) % 8;
            
            FlowDirection[] directions = {
                FlowDirection.East, FlowDirection.SouthEast, FlowDirection.South,
                FlowDirection.SouthWest, FlowDirection.West, FlowDirection.NorthWest,
                FlowDirection.North, FlowDirection.NorthEast
            };
            
            return directions[directionIndex];
        }
                            double distance = (k % 2 == 0) ? cellSize : cellSize * Math.Sqrt(2);
                            double slope = (elevationGrid[i, j] - elevationGrid[ni, nj]) / distance;

                            if (slope > maxSlope)
                            {
                                maxSlope = slope;
                                steepestDirection = directions[k];
                            }
                        }
                    }

                    flowDirections[i, j] = steepestDirection;
                }
            }
        }

        /// <summary>
        /// Calcula acumulación de flujo
        /// </summary>
        private void CalculateFlowAccumulation()
        {
            // Inicializar todas las celdas con 1 (área de la celda)
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    flowAccumulation[i, j] = double.IsNaN(elevationGrid[i, j]) ? 0 : 1;
                }
            }

            // Procesar en orden topológico (de mayor a menor elevación)
            var cellsByElevation = new List<(int i, int j, double elevation)>();
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    if (!double.IsNaN(elevationGrid[i, j]))
                    {
                        cellsByElevation.Add((i, j, elevationGrid[i, j]));
                    }
                }
            }

            cellsByElevation.Sort((a, b) => b.elevation.CompareTo(a.elevation));

            foreach (var cell in cellsByElevation)
            {
                int i = cell.i;
                int j = cell.j;
                var direction = flowDirections[i, j];

                if (direction != FlowDirection.None)
                {
                    var (ni, nj) = GetFlowTarget(i, j, direction);
                    if (ni >= 0 && ni < rows && nj >= 0 && nj < cols)
                    {
                        flowAccumulation[ni, nj] += flowAccumulation[i, j];
                    }
                }
            }
        }

        /// <summary>
        /// Obtiene la celda destino del flujo
        /// </summary>
        private (int, int) GetFlowTarget(int i, int j, FlowDirection direction)
        {
            switch (direction)
            {
                case FlowDirection.East: return (i, j + 1);
                case FlowDirection.SouthEast: return (i + 1, j + 1);
                case FlowDirection.South: return (i + 1, j);
                case FlowDirection.SouthWest: return (i + 1, j - 1);
                case FlowDirection.West: return (i, j - 1);
                case FlowDirection.NorthWest: return (i - 1, j - 1);
                case FlowDirection.North: return (i - 1, j);
                case FlowDirection.NorthEast: return (i - 1, j + 1);
                default: return (-1, -1);
            }
        }

        /// <summary>
        /// Identifica celdas con alta acumulación de flujo (potenciales cursos de agua)
        /// </summary>
        /// <param name="threshold">Umbral mínimo de acumulación</param>
        /// <returns>Lista de puntos de drenaje</returns>
        public List<(int row, int col, double accumulation)> IdentifyDrainagePoints(double threshold)
        {
            var drainagePoints = new List<(int, int, double)>();

            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    if (flowAccumulation[i, j] >= threshold)
                    {
                        drainagePoints.Add((i, j, flowAccumulation[i, j]));
                    }
                }
            }

            return drainagePoints.OrderByDescending(p => p.Item3).ToList();
        }

        /// <summary>
        /// Traza una línea de drenaje desde un punto dado
        /// </summary>
        /// <param name="startRow">Fila inicial</param>
        /// <param name="startCol">Columna inicial</param>
        /// <returns>Secuencia de puntos que forman la línea de drenaje</returns>
        public List<(int row, int col)> TraceDrainageLine(int startRow, int startCol)
        {
            var drainageLine = new List<(int, int)>();
            int currentRow = startRow;
            int currentCol = startCol;

            var visited = new HashSet<(int, int)>();

            while (currentRow >= 0 && currentRow < rows && 
                   currentCol >= 0 && currentCol < cols &&
                   !visited.Contains((currentRow, currentCol)))
            {
                visited.Add((currentRow, currentCol));
                drainageLine.Add((currentRow, currentCol));

                var direction = flowDirections[currentRow, currentCol];
                if (direction == FlowDirection.None) break;

                var (nextRow, nextCol) = GetFlowTarget(currentRow, currentCol, direction);
                currentRow = nextRow;
                currentCol = nextCol;
            }

            return drainageLine;
        }

        /// <summary>
        /// Propiedades de acceso a los datos calculados
        /// </summary>
        public double[,] ElevationGrid => elevationGrid;
        public FlowDirection[,] FlowDirections => flowDirections;
        public double[,] FlowAccumulation => flowAccumulation;
        public int Rows => rows;
        public int Cols => cols;
        public double CellSize => cellSize;
    }
}
