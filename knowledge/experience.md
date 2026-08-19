# Experiencia profesional y de investigación

## Criterio de interpretación de trayectoria

La experiencia documentada en las fuentes corresponde primordialmente a investigación aplicada de posgrado y actividades académicas universitarias. No debe presentarse como empleos corporativos ni atribuirle funciones laborales empresariales no confirmadas por las fuentes. `[SRC-CV-01]` `[SRC-MSC-THESIS-01]` `[SRC-PHD-THESIS-01]`

---

## 1. Investigador en Inteligencia Artificial Aplicada y Machine Learning

- **Contexto:** Doctorado en Ciencias de la Computación, Tecnológico Nacional de México, campus Culiacán.
- **Periodo:** Agosto de 2022 a agosto de 2026. La defensa de tesis y obtención del grado se realizaron el 10 de agosto de 2026. `[SRC-USER-CONFIRM-2026-08-18]`
- **Naturaleza:** Investigación de posgrado (Doctoral).

### Responsabilidades y actividades principales
- Diseñar e implementar un mecanismo inteligente de extremo a extremo para la detección, cuantificación geométrica y evaluación de severidad de baches y grietas en pavimentos flexibles.
- Adquirir, limpiar, organizar y anotar imágenes RGB, datos de profundidad y nubes de puntos 3D.
- Entrenar, optimizar y evaluar modelos de segmentación semántica basados en Transformers (SegFormer) y redes convolucionales (U-Net con codificador MiT-B2 y pérdida combinada Dice-BCE).
- Aplicar optimización de hiperparámetros con Optuna y validación cruzada agrupada por secuencia (*Grouped 5-Fold Cross-Validation*).
- Desarrollar canalizaciones geométricas para estimar diámetro y profundidad de baches (mediante proyección sobre nubes de puntos 3D y planos RANSAC) y anchura y longitud de grietas (mediante esqueletización, PCA y trazado de rayos subpíxel).
- Implementar seguimiento temporal de grietas con el algoritmo SORT.
- Evaluar la explicabilidad de los modelos mediante mapas de atención Grad-CAM y métricas CAM-IoU y ROAD.
- Construir e integrar sistemas de inferencia difusa (Mamdani) para traducir mediciones físicas en niveles de severidad y recomendaciones de reparación basadas en normas técnicas SICT.
- Redactar publicaciones científicas, reportes técnicos y el documento doctoral.

### Herramientas y métodos
Python, PyTorch (2.9.1), CUDA (12.8), SegFormer, U-Net, MiT-B2, Optuna, OpenCV, Open3D, SORT, RANSAC, PCA, Grad-CAM, CAM-IoU, ROAD, Intel RealSense D435i, GoPro HERO8 Black, 2 GPU NVIDIA GeForce RTX 4070 Ti, Nubes de Puntos 3D, Lógica Difusa.

### Resultados e impacto cuantitativo
- *Baches:* Dataset de 583 imágenes; segmentación con IoU de 85.87 %, Precisión de 90.01 % y F1 de 90.43 %. Cuantificación física probada en 11 muestras de campo con MAE de 3.73 cm (diámetro) y 7.02 mm (profundidad).
- *Grietas:* Dataset de 500 imágenes anotadas; segmentación con Dice global *out-of-fold* de 0.7415.
- *Sistema difuso:* Sus resultados se compararon utilizando el manual de evaluaciones de la SICT.
- *(Para el desarrollo detallado de la metodología y métricas, véase `knowledge/research.md`).* `[SRC-PHD-THESIS-01]`

---

## 2. Investigador en Visión por Computadora y Machine Learning

- **Contexto:** Maestría en Ciencias de la Computación, Tecnológico Nacional de México, campus Culiacán.
- **Periodo:** Agosto de 2020 a agosto de 2022.
- **Naturaleza:** Investigación de posgrado (Maestría).

### Responsabilidades y actividades principales
- Diseñar y desarrollar un sistema de visión por computadora para la extracción automatizada de características viales desde secuencias de video monoculares.
- Recolectar y etiquetar manualmente un conjunto de datos personalizado de 21,000 imágenes repartidas equitativamente en 7 clases usando LabelImg.
- Configurar, entrenar y evaluar modelos de detección de objetos basados en YOLOv3 y la arquitectura DarkNet.
- Integrar algoritmos de seguimiento de objetos y predicción de trayectorias mediante el Filtro de Kalman y el algoritmo AutoTrack.
- Formular la lógica de gestión de excepciones para resolver oclusiones temporales y reaparición de vehículos, reduciendo conteos duplicados.
- Construir un flujo modular en Python para procesar videos y exportar métricas viales (conteo, clasificación, distancia y tiempo) a archivos CSV.
- Configurar y desplegar entornos de experimentación reproducibles utilizando contenedores Docker con aceleración por GPU NVIDIA.

### Herramientas y métodos
Python, TensorFlow, DarkNet, YOLOv3, OpenCV, AutoTrack, Filtro de Kalman, Algoritmo Húngaro, Docker, NVIDIA Docker, Ubuntu Linux, LabelImg, Git/GitHub y 2 GPU NVIDIA GeForce RTX 2080 Ti.

### Resultados e impacto cuantitativo
- Dataset propio de 21,000 imágenes etiquetadas (3,000 por clase).
- Incremento de la precisión promedio global (mAP) de 25.62 % a 90.62 % tras 5 iteraciones de hiperparámetros.
- Precisión por clase de hasta 95.43 % (Van) y 93.22 % (Camioneta / Autobús).
- *(Para el desarrollo detallado de la metodología y métricas, véase `knowledge/research.md`).* `[SRC-MSC-THESIS-01]`

---

## 3. Asesor de Proyectos y Tesis de Licenciatura / Instructor

- **Contexto:** Actividad académica durante los estudios de posgrado en el Tecnológico Nacional de México, campus Culiacán.
- **Periodo declared:** Agosto de 2020 a la actualidad documentada.
- **Naturaleza:** Actividad académica vinculada a los estudios de posgrado. Las fuentes no permiten presentarla como una relación laboral, plaza docente o empleo empresarial formal. `[SRC-CV-01]`

### Actividades declaradas
- Asesorar a estudiantes de licenciatura en proyectos de desarrollo en Python, adquisición y etiquetado de datasets para inteligencia artificial.
- Guiar la selección de arquitecturas de aprendizaje profundo, la preparación de experimentos y la optimización de hiperparámetros.
- Orientar en la elección de métricas de evaluación (matriz de confusión, precisión, recall, F1, MAE) y en el análisis de errores.
- Apoyar en la redacción técnica de reportes, documentación de proyectos y comunicación de resultados. `[SRC-CV-01]`

### Resultados
No se disponen de cifras cuantitativas sobre la cantidad exacta de alumnos o tesis concluidas. No deben fabricarse datos no sustentados. `[SRC-CV-01]`
