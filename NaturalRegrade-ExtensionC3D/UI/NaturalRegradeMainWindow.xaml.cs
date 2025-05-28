#nullable disable
using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.Civil.ApplicationServices;
using Autodesk.Civil.DatabaseServices;
using NaturalRegrade_addon.Core;

namespace NaturalRegrade_addon.UI
{
    /// <summary>
    /// Ventana principal del plugin Natural Regrade con diseño moderno y profesional
    /// </summary>
    public partial class NaturalRegradeMainWindow : Window
    {
        public TinSurface SelectedSurface { get; private set; }
        public GeomorphicRegradeProcessor.ProcessingParameters ProcessingParameters { get; private set; }

        private List<TinSurface> availableSurfaces;

        public NaturalRegradeMainWindow()
        {
            InitializeComponent();
            LoadAvailableSurfaces();
            InitializeParameters();
            SetupEventHandlers();
        }

        /// <summary>
        /// Carga las superficies TIN disponibles
        /// </summary>
        private void LoadAvailableSurfaces()
        {
            try
            {
                availableSurfaces = new List<TinSurface>();
                
                var doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
                if (doc == null) return;

                var civilDoc = Autodesk.Civil.ApplicationServices.CivilApplication.ActiveDocument;
                var surfaceIds = civilDoc.GetSurfaceIds();

                using (var transaction = doc.TransactionManager.StartTransaction())
                {                foreach (ObjectId surfaceId in surfaceIds)
                {
                    var surface = transaction.GetObject(surfaceId, Autodesk.AutoCAD.DatabaseServices.OpenMode.ForRead) as TinSurface;
                        if (surface != null)
                        {
                            availableSurfaces.Add(surface);
                        }
                    }
                    transaction.Commit();
                }

                // Actualizar ComboBox
                SurfaceComboBox.ItemsSource = availableSurfaces;
                SurfaceComboBox.DisplayMemberPath = "Name";
                
                if (availableSurfaces.Count > 0)
                {
                    SurfaceComboBox.SelectedIndex = 0;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error cargando superficies: {ex.Message}", "Error", 
                              MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Inicializa parámetros por defecto
        /// </summary>
        private void InitializeParameters()
        {
            ProcessingParameters = new GeomorphicRegradeProcessor.ProcessingParameters();
            
            // Configurar controles con valores por defecto
            GridResolutionSlider.Value = ProcessingParameters.GridResolution;
            MinFlowAccumulationSlider.Value = ProcessingParameters.MinFlowAccumulation;
            SmoothingFactorSlider.Value = ProcessingParameters.SmoothingParams.SmoothingFactor;
            IterationsSlider.Value = ProcessingParameters.SmoothingParams.Iterations;
            MaxSlopeSlider.Value = ProcessingParameters.MaxStableSlope;
            
            OutputSurfaceNameTextBox.Text = ProcessingParameters.OutputSurfaceName;
            DrainageLayerNameTextBox.Text = ProcessingParameters.DrainageLayerName;
            ContourIntervalSlider.Value = ProcessingParameters.ContourInterval;
            
            PreserveDrainageCheckBox.IsChecked = ProcessingParameters.SmoothingParams.PreserveDrainage;
            CreateContoursCheckBox.IsChecked = ProcessingParameters.CreateContours;
            ValidateErosionCheckBox.IsChecked = ProcessingParameters.ValidateErosionResistance;
            GenerateReportCheckBox.IsChecked = ProcessingParameters.GenerateReport;
            AdaptiveSmoothingCheckBox.IsChecked = ProcessingParameters.SmoothingParams.UseAdaptiveSmoothing;

            UpdateParameterLabels();
        }

        /// <summary>
        /// Configura manejadores de eventos
        /// </summary>
        private void SetupEventHandlers()
        {
            GridResolutionSlider.ValueChanged += Slider_ValueChanged;
            MinFlowAccumulationSlider.ValueChanged += Slider_ValueChanged;
            SmoothingFactorSlider.ValueChanged += Slider_ValueChanged;
            IterationsSlider.ValueChanged += Slider_ValueChanged;
            MaxSlopeSlider.ValueChanged += Slider_ValueChanged;
            ContourIntervalSlider.ValueChanged += Slider_ValueChanged;
        }

        /// <summary>
        /// Actualiza las etiquetas de los parámetros
        /// </summary>
        private void UpdateParameterLabels()
        {
            GridResolutionLabel.Content = $"Resolución de Malla: {GridResolutionSlider.Value:F1} m";
            MinFlowAccumulationLabel.Content = $"Acumulación Mínima: {MinFlowAccumulationSlider.Value:F0}";
            SmoothingFactorLabel.Content = $"Factor de Suavizado: {SmoothingFactorSlider.Value:F2}";
            IterationsLabel.Content = $"Iteraciones: {IterationsSlider.Value:F0}";
            MaxSlopeLabel.Content = $"Pendiente Máxima: {MaxSlopeSlider.Value:F1}°";
            ContourIntervalLabel.Content = $"Intervalo de Contornos: {ContourIntervalSlider.Value:F1} m";
        }

        /// <summary>
        /// Manejador para cambios en sliders
        /// </summary>
        private void Slider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            UpdateParameterLabels();
        }

        /// <summary>
        /// Manejador para botón Ejecutar
        /// </summary>
        private void ExecuteButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Validar selección de superficie
                if (SurfaceComboBox.SelectedItem == null)
                {
                    MessageBox.Show("Por favor seleccione una superficie TIN para procesar.", 
                                  "Superficie Requerida", MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                SelectedSurface = SurfaceComboBox.SelectedItem as TinSurface;

                // Actualizar parámetros con valores de la interfaz
                UpdateParametersFromInterface();

                // Validar parámetros
                if (!ValidateParameters())
                {
                    return;
                }

                // Mostrar confirmación
                var confirmMessage = $"¿Está seguro de ejecutar Natural Regrade en la superficie '{SelectedSurface.Name}'?\n\n" +
                                   $"Parámetros principales:\n" +
                                   $"• Resolución: {ProcessingParameters.GridResolution} m\n" +
                                   $"• Factor de suavizado: {ProcessingParameters.SmoothingParams.SmoothingFactor}\n" +
                                   $"• Superficie de salida: {ProcessingParameters.OutputSurfaceName}";

                var result = MessageBox.Show(confirmMessage, "Confirmar Ejecución", 
                                           MessageBoxButton.YesNo, MessageBoxImage.Question);

                if (result == MessageBoxResult.Yes)
                {
                    DialogResult = true;
                    Close();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error preparando ejecución: {ex.Message}", "Error", 
                              MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Manejador para botón Cancelar
        /// </summary>
        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }

        /// <summary>
        /// Manejador para botón Restaurar Defaults
        /// </summary>
        private void RestoreDefaultsButton_Click(object sender, RoutedEventArgs e)
        {
            var result = MessageBox.Show("¿Está seguro de restaurar todos los parámetros a sus valores por defecto?", 
                                       "Restaurar Defaults", MessageBoxButton.YesNo, MessageBoxImage.Question);
            
            if (result == MessageBoxResult.Yes)
            {
                InitializeParameters();
            }
        }

        /// <summary>
        /// Manejador para botón Ayuda
        /// </summary>
        private void HelpButton_Click(object sender, RoutedEventArgs e)
        {
            var helpMessage = "NATURAL REGRADE - Ayuda\n\n" +
                            "Este plugin aplica técnicas de regrade geomorfológico para crear superficies naturales " +
                            "resistentes a la erosión, basado en metodología GeoFluv.\n\n" +
                            "PARÁMETROS PRINCIPALES:\n\n" +
                            "• Resolución de Malla: Tamaño de celda para análisis (menor = más detalle)\n" +
                            "• Acumulación Mínima: Umbral para identificar cursos de agua\n" +
                            "• Factor de Suavizado: Intensidad del suavizado (0-1)\n" +
                            "• Iteraciones: Número de pasadas del filtro de suavizado\n" +
                            "• Pendiente Máxima: Límite de estabilidad geotécnica\n\n" +
                            "OPCIONES AVANZADAS:\n\n" +
                            "• Preservar Drenaje: Mantiene líneas de agua durante suavizado\n" +
                            "• Suavizado Adaptativo: Ajusta intensidad según rugosidad local\n" +
                            "• Crear Contornos: Genera curvas de nivel automáticamente\n" +
                            "• Validar Erosión: Verifica resistencia a erosión del resultado\n\n" +
                            "Para más información, consulte la documentación técnica.";

            MessageBox.Show(helpMessage, "Ayuda - Natural Regrade", 
                          MessageBoxButton.OK, MessageBoxImage.Information);
        }

        /// <summary>
        /// Actualiza parámetros desde la interfaz
        /// </summary>
        private void UpdateParametersFromInterface()
        {
            ProcessingParameters.GridResolution = GridResolutionSlider.Value;
            ProcessingParameters.MinFlowAccumulation = MinFlowAccumulationSlider.Value;
            ProcessingParameters.SmoothingParams.SmoothingFactor = SmoothingFactorSlider.Value;
            ProcessingParameters.SmoothingParams.Iterations = (int)IterationsSlider.Value;
            ProcessingParameters.MaxStableSlope = MaxSlopeSlider.Value;
            ProcessingParameters.ContourInterval = ContourIntervalSlider.Value;

            ProcessingParameters.OutputSurfaceName = OutputSurfaceNameTextBox.Text.Trim();
            ProcessingParameters.DrainageLayerName = DrainageLayerNameTextBox.Text.Trim();

            ProcessingParameters.SmoothingParams.PreserveDrainage = PreserveDrainageCheckBox.IsChecked ?? true;
            ProcessingParameters.CreateContours = CreateContoursCheckBox.IsChecked ?? true;
            ProcessingParameters.ValidateErosionResistance = ValidateErosionCheckBox.IsChecked ?? true;
            ProcessingParameters.GenerateReport = GenerateReportCheckBox.IsChecked ?? true;
            ProcessingParameters.SmoothingParams.UseAdaptiveSmoothing = AdaptiveSmoothingCheckBox.IsChecked ?? true;
        }

        /// <summary>
        /// Valida parámetros de entrada
        /// </summary>
        private bool ValidateParameters()
        {
            // Validar nombre de superficie de salida
            if (string.IsNullOrWhiteSpace(ProcessingParameters.OutputSurfaceName))
            {
                MessageBox.Show("El nombre de la superficie de salida no puede estar vacío.", 
                              "Validación", MessageBoxButton.OK, MessageBoxImage.Warning);
                OutputSurfaceNameTextBox.Focus();
                return false;
            }

            // Validar nombre de capa de drenaje
            if (string.IsNullOrWhiteSpace(ProcessingParameters.DrainageLayerName))
            {
                MessageBox.Show("El nombre de la capa de drenaje no puede estar vacío.", 
                              "Validación", MessageBoxButton.OK, MessageBoxImage.Warning);
                DrainageLayerNameTextBox.Focus();
                return false;
            }

            // Validar nombres de AutoCAD (sin caracteres especiales)
            if (!IsValidAutoCADName(ProcessingParameters.OutputSurfaceName))
            {
                MessageBox.Show("El nombre de la superficie contiene caracteres no válidos para AutoCAD.", 
                              "Validación", MessageBoxButton.OK, MessageBoxImage.Warning);
                OutputSurfaceNameTextBox.Focus();
                return false;
            }

            if (!IsValidAutoCADName(ProcessingParameters.DrainageLayerName))
            {
                MessageBox.Show("El nombre de la capa contiene caracteres no válidos para AutoCAD.", 
                              "Validación", MessageBoxButton.OK, MessageBoxImage.Warning);
                DrainageLayerNameTextBox.Focus();
                return false;
            }

            return true;
        }

        /// <summary>
        /// Valida si un nombre es válido para AutoCAD
        /// </summary>
        private bool IsValidAutoCADName(string name)
        {
            if (string.IsNullOrWhiteSpace(name)) return false;
            
            // Caracteres no permitidos en nombres de AutoCAD
            char[] invalidChars = { '<', '>', '/', '\\', '"', ':', ';', '?', '*', '|', '=', '`' };
            
            return !name.Any(c => invalidChars.Contains(c)) && 
                   name.Length <= 255 && // Límite de AutoCAD
                   !name.StartsWith(" ") && 
                   !name.EndsWith(" ");
        }

        /// <summary>
        /// Manejador para vista previa de parámetros
        /// </summary>
        private void PreviewButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (SurfaceComboBox.SelectedItem == null)
                {
                    MessageBox.Show("Seleccione una superficie para ver la vista previa.", 
                                  "Superficie Requerida", MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                UpdateParametersFromInterface();

                var previewWindow = new ParametersPreviewWindow(ProcessingParameters);
                previewWindow.Owner = this;
                previewWindow.ShowDialog();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error mostrando vista previa: {ex.Message}", "Error", 
                              MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
    }

    /// <summary>
    /// Ventana de vista previa de parámetros
    /// </summary>
    public class ParametersPreviewWindow : Window
    {
        private GeomorphicRegradeProcessor.ProcessingParameters parameters;

        public ParametersPreviewWindow(GeomorphicRegradeProcessor.ProcessingParameters parameters)
        {
            this.parameters = parameters;
            InitializeWindow();
            LoadParameters();
        }

        private void InitializeWindow()
        {
            Title = "Vista Previa de Parámetros - Natural Regrade";
            Width = 500;
            Height = 600;
            WindowStartupLocation = WindowStartupLocation.CenterOwner;
            ResizeMode = ResizeMode.NoResize;

            var scrollViewer = new ScrollViewer
            {
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                Padding = new Thickness(10)
            };

            var stackPanel = new StackPanel();
            scrollViewer.Content = stackPanel;
            Content = scrollViewer;            // Título
            var titleLabel = new System.Windows.Controls.Label
            {
                Content = "Resumen de Parámetros de Procesamiento",
                FontSize = 16,
                FontWeight = FontWeights.Bold,
                HorizontalAlignment = HorizontalAlignment.Center,
                Margin = new Thickness(0, 0, 0, 20)
            };
            stackPanel.Children.Add(titleLabel);

            // Crear secciones de parámetros
            AddParameterSection(stackPanel, "PARÁMETROS HIDROLÓGICOS", new[]
            {
                $"Resolución de Malla: {parameters.GridResolution:F1} m",
                $"Acumulación Mínima de Flujo: {parameters.MinFlowAccumulation:F0}",
                $"Distancia de Buffer de Drenaje: {parameters.DrainageBufferDistance:F1} m"
            });

            AddParameterSection(stackPanel, "PARÁMETROS DE SUAVIZADO", new[]
            {
                $"Factor de Suavizado: {parameters.SmoothingParams.SmoothingFactor:F2}",
                $"Número de Iteraciones: {parameters.SmoothingParams.Iterations}",
                $"Preservar Drenaje: {(parameters.SmoothingParams.PreserveDrainage ? "Sí" : "No")}",
                $"Suavizado Adaptativo: {(parameters.SmoothingParams.UseAdaptiveSmoothing ? "Sí" : "No")}",
                $"Preservación de Pendientes: {parameters.SmoothingParams.SlopePreservation:F2}",
                $"Umbral de Pendiente Crítica: {parameters.SmoothingParams.CriticalSlopeThreshold:F1}°"
            });

            AddParameterSection(stackPanel, "PARÁMETROS GEOMORFOLÓGICOS", new[]
            {
                $"Sinuosidad Objetivo: {parameters.TargetSinuosity:F1}",
                $"Pendiente Máxima Estable: {parameters.MaxStableSlope:F1}°",
                $"Pendiente Mínima de Drenaje: {parameters.MinDrainageSlope:F1}%"
            });

            AddParameterSection(stackPanel, "CONFIGURACIÓN DE SALIDA", new[]
            {
                $"Nombre de Superficie: {parameters.OutputSurfaceName}",
                $"Capa de Drenaje: {parameters.DrainageLayerName}",
                $"Crear Contornos: {(parameters.CreateContours ? "Sí" : "No")}",
                $"Intervalo de Contornos: {parameters.ContourInterval:F1} m"
            });

            AddParameterSection(stackPanel, "VALIDACIÓN Y REPORTES", new[]
            {
                $"Validar Resistencia a Erosión: {(parameters.ValidateErosionResistance ? "Sí" : "No")}",
                $"Generar Reporte: {(parameters.GenerateReport ? "Sí" : "No")}"
            });

            // Botón OK
            var okButton = new Button
            {
                Content = "OK",
                Width = 80,
                Height = 30,
                Margin = new Thickness(0, 20, 0, 0),
                HorizontalAlignment = HorizontalAlignment.Center
            };
            okButton.Click += (s, e) => Close();
            stackPanel.Children.Add(okButton);
        }

        private void AddParameterSection(StackPanel parent, string title, string[] parameters)
        {            // Título de sección
            var sectionTitle = new System.Windows.Controls.Label
            {
                Content = title,
                FontWeight = FontWeights.Bold,
                FontSize = 12,
                Background = System.Windows.Media.Brushes.LightGray,
                Margin = new Thickness(0, 10, 0, 5)
            };
            parent.Children.Add(sectionTitle);            // Parámetros
            foreach (var param in parameters)
            {
                var paramLabel = new System.Windows.Controls.Label
                {
                    Content = "  • " + param,
                    Margin = new Thickness(10, 0, 0, 0)
                };
                parent.Children.Add(paramLabel);
            }
        }

        private void LoadParameters()
        {
            // Los parámetros ya se cargan en InitializeWindow
        }
    }
}
