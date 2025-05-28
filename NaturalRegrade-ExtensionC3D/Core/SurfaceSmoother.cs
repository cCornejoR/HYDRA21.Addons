using System;
using System.Collections.Generic;
using MathNet.Numerics.LinearAlgebra;
using MathNet.Numerics.LinearAlgebra.Double;

namespace NaturalRegrade_addon.Core
{
    /// <summary>
    /// Suavizador de superficies usando algoritmos geomorfológicos avanzados
    /// Implementa filtros Laplacianos y Gaussianos adaptados para diseño de paisajes naturales
    /// Basado en principios de Bugosh & Epp (2019) y Zhang et al. (2018)
    /// </summary>
    public class SurfaceSmoother
    {
        private double[,] originalElevations;
        private double[,] smoothedElevations;
        private bool[,] drainageMask;
        private int rows, cols;
        private double cellSize;

        /// <summary>
        /// Parámetros de suavizado configurables
        /// </summary>
        public class SmoothingParameters
        {
            /// <summary>
            /// Factor de suavizado general (0.0 - 1.0)
            /// </summary>
            public double SmoothingFactor { get; set; } = 0.3;

            /// <summary>
            /// Número de iteraciones del filtro
            /// </summary>
            public int Iterations { get; set; } = 5;

            /// <summary>
            /// Preservar líneas de drenaje durante el suavizado
            /// </summary>
            public bool PreserveDrainage { get; set; } = true;

            /// <summary>
            /// Factor de preservación de pendientes naturales (0.0 - 1.0)
            /// </summary>
            public double SlopePreservation { get; set; } = 0.7;

            /// <summary>
            /// Umbral de pendiente para areas críticas (grados)
            /// </summary>
            public double CriticalSlopeThreshold { get; set; } = 30.0;

            /// <summary>
            /// Aplicar suavizado adaptativo basado en rugosidad local
            /// </summary>
            public bool UseAdaptiveSmoothing { get; set; } = true;

            /// <summary>
            /// Factor de anisotropía para direcciones preferenciales
            /// </summary>
            public double AnisotropyFactor { get; set; } = 1.2;
        }

        /// <summary>
        /// Inicializa el suavizador con datos de elevación
        /// </summary>
        /// <param name="elevationGrid">Malla de elevaciones</param>
        /// <param name="gridCellSize">Tamaño de celda en metros</param>
        public void Initialize(double[,] elevationGrid, double gridCellSize)
        {
            if (elevationGrid == null)
                throw new ArgumentNullException(nameof(elevationGrid));

            rows = elevationGrid.GetLength(0);
            cols = elevationGrid.GetLength(1);
            cellSize = gridCellSize;

            originalElevations = new double[rows, cols];
            smoothedElevations = new double[rows, cols];
            drainageMask = new bool[rows, cols];

            // Copiar datos originales
            Array.Copy(elevationGrid, originalElevations, elevationGrid.Length);
            Array.Copy(elevationGrid, smoothedElevations, elevationGrid.Length);
        }

        /// <summary>
        /// Establece máscara de drenaje para preservar líneas de agua
        /// </summary>
        /// <param name="drainagePoints">Lista de puntos de drenaje</param>
        /// <param name="bufferDistance">Distancia de buffer alrededor de líneas de drenaje</param>
        public void SetDrainageMask(List<(int row, int col)> drainagePoints, double bufferDistance = 2.0)
        {
            // Inicializar máscara
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    drainageMask[i, j] = false;
                }
            }

            // Marcar puntos de drenaje y su buffer
            int bufferCells = (int)Math.Ceiling(bufferDistance / cellSize);

            foreach (var (row, col) in drainagePoints)
            {
                for (int di = -bufferCells; di <= bufferCells; di++)
                {
                    for (int dj = -bufferCells; dj <= bufferCells; dj++)
                    {
                        int ni = row + di;
                        int nj = col + dj;

                        if (ni >= 0 && ni < rows && nj >= 0 && nj < cols)
                        {
                            double distance = Math.Sqrt(di * di + dj * dj) * cellSize;
                            if (distance <= bufferDistance)
                            {
                                drainageMask[ni, nj] = true;
                            }
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Aplica suavizado geomorfológico avanzado
        /// </summary>
        /// <param name="parameters">Parámetros de suavizado</param>
        /// <returns>Malla de elevaciones suavizada</returns>
        public double[,] ApplyGeomorphicSmoothing(SmoothingParameters parameters)
        {
            try
            {
                // 1. Calcular rugosidad local para suavizado adaptativo
                var roughnessMap = CalculateLocalRoughness();

                // 2. Aplicar filtros iterativamente
                for (int iteration = 0; iteration < parameters.Iterations; iteration++)
                {
                    if (parameters.UseAdaptiveSmoothing)
                    {
                        ApplyAdaptiveLaplacianFilter(parameters, roughnessMap);
                    }
                    else
                    {
                        ApplyStandardLaplacianFilter(parameters);
                    }

                    // 3. Aplicar suavizado gaussiano para transiciones naturales
                    ApplyGaussianFilter(parameters.SmoothingFactor * 0.5);

                    // 4. Preservar características críticas
                    PreserveCriticalFeatures(parameters);

                    // 5. Aplicar corrección de pendientes
                    ApplySlopeCorrection(parameters);
                }

                // 6. Post-procesamiento: asegurar flujo hacia drenajes
                EnsureDrainageFlow();

                return smoothedElevations;
            }
            catch (Exception ex)
            {
                throw new Exception($"Error en suavizado geomorfológico: {ex.Message}");
            }
        }

        /// <summary>
        /// Calcula mapa de rugosidad local para suavizado adaptativo
        /// </summary>
        private double[,] CalculateLocalRoughness()
        {
            var roughness = new double[rows, cols];

            for (int i = 1; i < rows - 1; i++)
            {
                for (int j = 1; j < cols - 1; j++)
                {
                    if (double.IsNaN(originalElevations[i, j])) continue;

                    // Calcular varianza local (ventana 3x3)
                    double sum = 0;
                    double sumSquares = 0;
                    int count = 0;

                    for (int di = -1; di <= 1; di++)
                    {
                        for (int dj = -1; dj <= 1; dj++)
                        {
                            int ni = i + di;
                            int nj = j + dj;

                            if (!double.IsNaN(originalElevations[ni, nj]))
                            {
                                double elevation = originalElevations[ni, nj];
                                sum += elevation;
                                sumSquares += elevation * elevation;
                                count++;
                            }
                        }
                    }

                    if (count > 0)
                    {
                        double mean = sum / count;
                        double variance = (sumSquares / count) - (mean * mean);
                        roughness[i, j] = Math.Sqrt(variance);
                    }
                }
            }

            return roughness;
        }

        /// <summary>
        /// Aplica filtro Laplaciano adaptativo
        /// </summary>
        private void ApplyAdaptiveLaplacianFilter(SmoothingParameters parameters, double[,] roughnessMap)
        {
            var newElevations = new double[rows, cols];
            Array.Copy(smoothedElevations, newElevations, smoothedElevations.Length);

            for (int i = 1; i < rows - 1; i++)
            {
                for (int j = 1; j < cols - 1; j++)
                {
                    if (double.IsNaN(smoothedElevations[i, j])) continue;
                    if (parameters.PreserveDrainage && drainageMask[i, j]) continue;

                    // Factor de suavizado adaptativo basado en rugosidad
                    double localRoughness = roughnessMap[i, j];
                    double maxRoughness = GetMaxRoughness(roughnessMap);
                    double adaptiveFactor = parameters.SmoothingFactor * 
                                          (1.0 + (localRoughness / maxRoughness));

                    // Aplicar filtro Laplaciano con anisotropía
                    double laplacian = CalculateAnisotropicLaplacian(i, j, parameters.AnisotropyFactor);
                    newElevations[i, j] = smoothedElevations[i, j] + adaptiveFactor * laplacian;
                }
            }

            smoothedElevations = newElevations;
        }

        /// <summary>
        /// Aplica filtro Laplaciano estándar
        /// </summary>
        private void ApplyStandardLaplacianFilter(SmoothingParameters parameters)
        {
            var newElevations = new double[rows, cols];
            Array.Copy(smoothedElevations, newElevations, smoothedElevations.Length);

            for (int i = 1; i < rows - 1; i++)
            {
                for (int j = 1; j < cols - 1; j++)
                {
                    if (double.IsNaN(smoothedElevations[i, j])) continue;
                    if (parameters.PreserveDrainage && drainageMask[i, j]) continue;

                    double laplacian = CalculateStandardLaplacian(i, j);
                    newElevations[i, j] = smoothedElevations[i, j] + 
                                        parameters.SmoothingFactor * laplacian;
                }
            }

            smoothedElevations = newElevations;
        }

        /// <summary>
        /// Calcula Laplaciano anisotrópico para direcciones preferenciales
        /// </summary>
        private double CalculateAnisotropicLaplacian(int i, int j, double anisotropyFactor)
        {
            // Pesos anisotrópicos (mayor peso en direcciones N-S para simular flujo gravitacional)
            double[,] weights = {
                { 0.5, anisotropyFactor, 0.5 },
                { 1.0, -4.0 * anisotropyFactor, 1.0 },
                { 0.5, anisotropyFactor, 0.5 }
            };

            double laplacian = 0;
            for (int di = -1; di <= 1; di++)
            {
                for (int dj = -1; dj <= 1; dj++)
                {
                    int ni = i + di;
                    int nj = j + dj;

                    if (ni >= 0 && ni < rows && nj >= 0 && nj < cols &&
                        !double.IsNaN(smoothedElevations[ni, nj]))
                    {
                        laplacian += weights[di + 1, dj + 1] * smoothedElevations[ni, nj];
                    }
                }
            }

            return laplacian;
        }

        /// <summary>
        /// Calcula Laplaciano estándar
        /// </summary>
        private double CalculateStandardLaplacian(int i, int j)
        {
            double sum = 0;
            int count = 0;

            // Vecinos cardinales
            int[] di = { -1, 1, 0, 0 };
            int[] dj = { 0, 0, -1, 1 };

            for (int k = 0; k < 4; k++)
            {
                int ni = i + di[k];
                int nj = j + dj[k];

                if (ni >= 0 && ni < rows && nj >= 0 && nj < cols &&
                    !double.IsNaN(smoothedElevations[ni, nj]))
                {
                    sum += smoothedElevations[ni, nj];
                    count++;
                }
            }

            return count > 0 ? (sum / count) - smoothedElevations[i, j] : 0;
        }

        /// <summary>
        /// Aplica filtro Gaussiano para transiciones suaves
        /// </summary>
        private void ApplyGaussianFilter(double sigma)
        {
            int kernelSize = (int)(3 * sigma) * 2 + 1;
            var kernel = CreateGaussianKernel(kernelSize, sigma);
            var newElevations = new double[rows, cols];

            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    if (double.IsNaN(smoothedElevations[i, j]))
                    {
                        newElevations[i, j] = smoothedElevations[i, j];
                        continue;
                    }

                    double weightedSum = 0;
                    double totalWeight = 0;
                    int halfKernel = kernelSize / 2;

                    for (int ki = 0; ki < kernelSize; ki++)
                    {
                        for (int kj = 0; kj < kernelSize; kj++)
                        {
                            int ni = i + ki - halfKernel;
                            int nj = j + kj - halfKernel;

                            if (ni >= 0 && ni < rows && nj >= 0 && nj < cols &&
                                !double.IsNaN(smoothedElevations[ni, nj]))
                            {
                                double weight = kernel[ki, kj];
                                weightedSum += weight * smoothedElevations[ni, nj];
                                totalWeight += weight;
                            }
                        }
                    }

                    newElevations[i, j] = totalWeight > 0 ? weightedSum / totalWeight : 
                                        smoothedElevations[i, j];
                }
            }

            smoothedElevations = newElevations;
        }

        /// <summary>
        /// Crea kernel Gaussiano
        /// </summary>
        private double[,] CreateGaussianKernel(int size, double sigma)
        {
            var kernel = new double[size, size];
            double sum = 0;
            int center = size / 2;

            for (int i = 0; i < size; i++)
            {
                for (int j = 0; j < size; j++)
                {
                    double x = i - center;
                    double y = j - center;
                    double value = Math.Exp(-(x * x + y * y) / (2 * sigma * sigma));
                    kernel[i, j] = value;
                    sum += value;
                }
            }

            // Normalizar
            for (int i = 0; i < size; i++)
            {
                for (int j = 0; j < size; j++)
                {
                    kernel[i, j] /= sum;
                }
            }

            return kernel;
        }

        /// <summary>
        /// Preserva características críticas durante el suavizado
        /// </summary>
        private void PreserveCriticalFeatures(SmoothingParameters parameters)
        {
            for (int i = 1; i < rows - 1; i++)
            {
                for (int j = 1; j < cols - 1; j++)
                {
                    if (double.IsNaN(smoothedElevations[i, j])) continue;

                    // Calcular pendiente local
                    double slope = CalculateLocalSlope(i, j);
                    
                    // Si la pendiente es crítica, reducir el suavizado
                    if (slope > parameters.CriticalSlopeThreshold)
                    {
                        double preservationFactor = parameters.SlopePreservation;
                        smoothedElevations[i, j] = originalElevations[i, j] * preservationFactor +
                                                 smoothedElevations[i, j] * (1 - preservationFactor);
                    }
                }
            }
        }

        /// <summary>
        /// Aplica corrección de pendientes para estabilidad
        /// </summary>
        private void ApplySlopeCorrection(SmoothingParameters parameters)
        {
            const double maxStableSlope = 35.0; // grados

            for (int i = 1; i < rows - 1; i++)
            {
                for (int j = 1; j < cols - 1; j++)
                {
                    if (double.IsNaN(smoothedElevations[i, j])) continue;

                    double slope = CalculateLocalSlope(i, j);
                    
                    if (slope > maxStableSlope)
                    {
                        // Reducir pendiente gradualmente
                        AdjustSlopeForStability(i, j, maxStableSlope);
                    }
                }
            }
        }

        /// <summary>
        /// Calcula pendiente local en grados
        /// </summary>
        private double CalculateLocalSlope(int i, int j)
        {
            double dx = (smoothedElevations[i, j + 1] - smoothedElevations[i, j - 1]) / (2 * cellSize);
            double dy = (smoothedElevations[i - 1, j] - smoothedElevations[i + 1, j]) / (2 * cellSize);
            
            double slopeRadians = Math.Atan(Math.Sqrt(dx * dx + dy * dy));
            return slopeRadians * 180.0 / Math.PI;
        }

        /// <summary>
        /// Ajusta pendiente para estabilidad geotécnica
        /// </summary>
        private void AdjustSlopeForStability(int i, int j, double maxSlope)
        {
            // Implementación simplificada - ajustar elevación para cumplir pendiente máxima
            double averageNeighborElevation = 0;
            int count = 0;

            for (int di = -1; di <= 1; di++)
            {
                for (int dj = -1; dj <= 1; dj++)
                {
                    if (di == 0 && dj == 0) continue;

                    int ni = i + di;
                    int nj = j + dj;

                    if (ni >= 0 && ni < rows && nj >= 0 && nj < cols &&
                        !double.IsNaN(smoothedElevations[ni, nj]))
                    {
                        averageNeighborElevation += smoothedElevations[ni, nj];
                        count++;
                    }
                }
            }

            if (count > 0)
            {
                averageNeighborElevation /= count;
                double maxElevationDiff = Math.Tan(maxSlope * Math.PI / 180.0) * cellSize;
                
                // Limitar diferencia de elevación
                if (Math.Abs(smoothedElevations[i, j] - averageNeighborElevation) > maxElevationDiff)
                {
                    smoothedElevations[i, j] = averageNeighborElevation + 
                        Math.Sign(smoothedElevations[i, j] - averageNeighborElevation) * maxElevationDiff;
                }
            }
        }

        /// <summary>
        /// Asegura que el flujo se dirija hacia las líneas de drenaje
        /// </summary>
        private void EnsureDrainageFlow()
        {
            // Aplicar gradiente hacia líneas de drenaje
            for (int i = 1; i < rows - 1; i++)
            {
                for (int j = 1; j < cols - 1; j++)
                {
                    if (double.IsNaN(smoothedElevations[i, j]) || drainageMask[i, j]) continue;

                    // Encontrar la línea de drenaje más cercana
                    var (drainageRow, drainageCol, distance) = FindNearestDrainage(i, j);
                    
                    if (distance < 10 * cellSize) // Dentro de zona de influencia
                    {
                        // Ajustar elevación para crear gradiente suave hacia drenaje
                        double drainageElevation = smoothedElevations[drainageRow, drainageCol];
                        double currentElevation = smoothedElevations[i, j];
                        
                        if (currentElevation <= drainageElevation)
                        {
                            // Crear pendiente mínima hacia el drenaje (0.5%)
                            double minSlope = 0.005; // 0.5%
                            smoothedElevations[i, j] = drainageElevation + distance * minSlope;
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Encuentra la línea de drenaje más cercana
        /// </summary>
        private (int row, int col, double distance) FindNearestDrainage(int i, int j)
        {
            double minDistance = double.MaxValue;
            int nearestRow = i;
            int nearestCol = j;

            for (int di = -20; di <= 20; di++) // Buscar en radio limitado
            {
                for (int dj = -20; dj <= 20; dj++)
                {
                    int ni = i + di;
                    int nj = j + dj;

                    if (ni >= 0 && ni < rows && nj >= 0 && nj < cols && drainageMask[ni, nj])
                    {
                        double distance = Math.Sqrt(di * di + dj * dj) * cellSize;
                        if (distance < minDistance)
                        {
                            minDistance = distance;
                            nearestRow = ni;
                            nearestCol = nj;
                        }
                    }
                }
            }

            return (nearestRow, nearestCol, minDistance);
        }

        /// <summary>
        /// Obtiene la rugosidad máxima del mapa
        /// </summary>
        private double GetMaxRoughness(double[,] roughnessMap)
        {
            double maxRoughness = 0;
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++)
                {
                    if (roughnessMap[i, j] > maxRoughness)
                    {
                        maxRoughness = roughnessMap[i, j];
                    }
                }
            }
            return Math.Max(maxRoughness, 1e-6); // Evitar división por cero
        }

        /// <summary>
        /// Propiedades de acceso
        /// </summary>
        public double[,] SmoothedElevations => smoothedElevations;
        public double[,] OriginalElevations => originalElevations;
    }
}
