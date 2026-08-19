# Investigaciones principales

Este documento contiene la síntesis estructurada de las principales investigaciones desarrolladas por Mario Alberto Román Garay. Se centra exclusivamente en aportaciones personales, metodología, modelos, datos, métricas y decisiones técnicas verificables a partir de las fuentes primarias. `[SRC-MSC-THESIS-01]` `[SRC-PHD-THESIS-01]`

---

## 1. Investigación Doctoral — Mecanismo inteligente para la evaluación de baches y grietas en pavimentos flexibles

- **Título:** *Mecanismo inteligente para la detección, clasificación y evaluación de deterioros de severidad media por agrietamiento y baches en pavimentos flexibles*.
- **Grado académico relacionado:** Doctor en Ciencias de la Computación. Defensa de tesis y obtención del grado: 10 de agosto de 2026. `[SRC-USER-CONFIRM-2026-08-18]`
- **Institución:** Tecnológico Nacional de México / Instituto Tecnológico de Culiacán, Departamento Académico de Estudios de Posgrado.
- **Periodo:** Agosto de 2022 a agosto de 2026.

### Problema, motivación y objetivo

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

**Problema investigado:** La inspección visual manual de baches y grietas en pavimentos flexibles es lenta, riesgosa para el personal en tránsito activo y propensa a variabilidad subjetiva entre evaluadores. Además, la simple detección visual 2D no provee las dimensiones físicas ni la severidad técnica requeridas para fundamentar decisiones de mantenimiento de infraestructura vial.

**Motivación:** Automatizar y estandarizar la cadena completa de auscultación vial, transformando datos brutos de sensores de campo en recomendaciones de ingeniería explicables y estructuradas, alineadas con la normativa técnica de la Secretaría de Infraestructura, Comunicaciones y Transportes (SICT).

**Objetivo:** Desarrollar un mecanismo inteligente de extremo a extremo que integre la adquisición de datos de campo, segmentación semántica, cuantificación geométrica tridimensional y bidimensional, evaluación de severidad y generación automatizada de recomendaciones de mantenimiento para baches y grietas en pavimentos flexibles.

### Aportación personal

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

Mario es el autor del trabajo doctoral. Diseñó e implementó la arquitectura completa de ambos módulos (baches y grietas), construyó y anotó los conjuntos de datos, desarrolló la tubería de integración 2D/3D con nubes de puntos y RANSAC para baches, la canalización de esqueletización, PCA y trazado de rayos subpíxel para grietas, la optimización de hiperparámetros con Optuna, las métricas de explicabilidad visual (Grad-CAM/CAM-IoU/ROAD) y la formulación de las bases de reglas en los sistemas de inferencia difusa.

### Metodología

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

  1. *Módulo de baches:* Adquisición RGB-D sobre vehículo $\rightarrow$ Alineación y estimación del plano de pavimento con RANSAC $\rightarrow$ Segmentación semántica 2D de la cavidad $\rightarrow$ Proyección de la máscara sobre la nube de puntos 3D $\rightarrow$ Extracción de diámetro y profundidad $\rightarrow$ Sistema de inferencia difusa para severidad y mantenimiento.
  2. *Módulo de grietas:* Adquisición RGB alta resolución $\rightarrow$ Extracción de parches ($512 \times 512$ px, solapamiento 64 px) $\rightarrow$ Segmentación semántica $\rightarrow$ Seguimiento temporal de grietas entre fotogramas con SORT $\rightarrow$ Esqueletización y orientación local con PCA $\rightarrow$ Medición ortogonal de anchura y longitud física $\rightarrow$ Sistema difuso jerárquico de 3 etapas para severidad final.

### Modelos y algoritmos utilizados

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

  - *Segmentación:* SegFormer para baches; U-Net con codificador MiT-B2 preentrenado en ImageNet para grietas.
  - *Función de pérdida:* Combinada Dice + Binary Cross-Entropy (Dice-BCE) para manejar desbalance extremo de clases en grietas.
  - *Geometría y seguimiento:* RANSAC (ajuste de planos 3D), Esqueletización morfológica, Análisis de Componentes Principales (PCA para orientación local), Trazado de rayos subpíxel, Algoritmo SORT (Simple Online and Realtime Tracking) para seguimiento multiobjeto.
  - *Explicabilidad:* Grad-CAM, CAM-IoU y ROAD.
  - *Toma de decisiones:* Sistemas de Inferencia Difusa (Mamdani) calibrados con normas técnicas SICT.

### Software, lenguajes, bibliotecas y hardware

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

  - *Lenguajes y bibliotecas:* Python, PyTorch (2.9.1), Segmentation Models PyTorch (smp), OpenCV, scikit-learn, SciPy, Open3D, NumPy, pandas, Optuna.
  - *Entorno:* Linux / Ubuntu, CUDA (12.8), Docker.
  - *Hardware de procesamiento:* CPU Intel i7, 32 GB RAM y 2 GPU NVIDIA GeForce RTX 4070 Ti.
  - *Dispositivos de adquisición:* Cámara RGB-D Intel RealSense D435i, cámara de acción GoPro HERO8 Black.

### Datos, pruebas y experimentos

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

  - *Dataset de baches:* 583 imágenes RGB-D anotadas. Validación física con 11 muestras de campo medidas manualmente (regla metálica y calibrador).
  - *Dataset de grietas:* 500 imágenes anotadas de alta resolución divididas en parches $512 \times 512$. Esquema de evaluación mediante *Grouped 5-Fold Cross-Validation* (Validación cruzada agrupada por secuencia para evitar fuga de datos entre fotogramas contiguos).
  - *Optimización:* Evaluación de 20 configuraciones de arquitectura/codificador/pérdida mediante Optuna.
  - *Comparación del sistema difuso:* Los resultados del sistema difuso se compararon utilizando el manual de evaluaciones de la SICT.

### Resultados y métricas verificables

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

  - *Segmentación de baches (SegFormer):* IoU = 85.872 %, Recall = 90.87 %, Precisión = 90.01 %, F1-score = 90.433 %.
  - *Cuantificación física de baches (11 muestras):* MAE de diámetro = 3.73 cm (RMSE = 4.78 cm); MAE de profundidad = 7.02 mm (RMSE = 7.91 mm).
  - *Segmentación de grietas (U-Net + MiT-B2):* Dice global *out-of-fold* = 0.7415.
  - *Cuantificación física de grietas:* Error relativo medio absoluto: Anchura = 24.15 % (RMSE = 3.68 mm); Longitud = 36.31 % (RMSE = 2193.59 mm).

### Decisiones técnicas relevantes

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

  - Empleo de SegFormer para baches debido a su atención global en cavidades anchas, y U-Net con MiT-B2 para grietas dada su alta retención de detalles finos y bordes delgados.
  - Adopción de *Grouped Cross-Validation* a nivel de video/escena para evitar sobreestimación de métricas por redundancia temporal.
  - Separación explícita del aprendizaje profundo (limitado a segmentación) y la inferencia difusa determinista para la toma de decisiones, garantizando explicabilidad y auditabilidad para ingenieros civiles.

### Dificultades y limitaciones

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

**Dificultades encontradas:**

  - Desbalance severo entre píxeles de fondo y píxeles de grieta fina.
  - Variaciones ambientales severas (sombras pronunciadas, pavimentos húmedos, escombros, iluminación solar directa).
  - Ruido en sensores de profundidad de consumo (Intel RealSense D435i) al medir cavidades en asfalto rugoso.

**Limitaciones:**

  - Los sensores RGB-D no ofrecen resolución suficiente para medir la profundidad milimétrica de grietas estrechas, limitando el módulo de grietas a mediciones 2D (anchura y longitud).
  - Tamaño de muestra física de baches acotado a 11 mediciones manuales de referencia.
  - El procesamiento se evaluó en diferido (*offline*) tras la recolección de datos; no se validó el despliegue en tiempo real a bordo del vehículo.

### Aprendizajes y relaciones

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

**Aprendizajes:**

  - La cuantificación física de deterioros requiere adaptar la modalidad sensorial a la geometría del daño (RGB-D para baches volumétricos, RGB calibrado para agrietamientos morfológicos).
  - Combinar Deep Learning con modelos de decisión basados en lógica difusa permite mantener la trazabilidad normativa sin depender de etiquetas subjetivas de severidad durante el entrenamiento.

**Publicaciones o proyectos relacionados:** `PUB-02`, `PUB-03`, `PJT-01`.

### Preguntas profesionales respaldadas

> Contexto de recuperación: Investigación doctoral · Fuente principal: `[SRC-PHD-THESIS-01]`

  - ¿Qué experiencia tiene en diseño de arquitecturas de IA aplicada combinando Visión por Computadora, Deep Learning y Lógica Difusa?
  - ¿Cómo aborda el desbalance de clases y la fuga de datos en modelos de segmentación semántica?
  - ¿Ha trabajado con sensores 3D, nubes de puntos y modelos Transformers en PyTorch?
  - ¿Cómo valida y evalúa cuantitativamente modelos de IA frente a mediciones físicas del mundo real?

---

## 2. Investigación de Maestría — Sistema generador de información vial a partir de secuencia de imágenes

- **Título:** *Sistema generador de información vial a partir de secuencia de imágenes*.
- **Grado académico relacionado:** Maestro en Ciencias de la Computación (Grado obtenido en agosto de 2022).
- **Institución:** Tecnológico Nacional de México / Instituto Tecnológico de Culiacán, Departamento Académico de Estudios de Posgrado.
- **Periodo:** Agosto de 2020 a agosto de 2022.

### Problema, motivación y objetivo

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

**Problema investigado:** La recolección de aforos y métricas de tránsito vehicular (conteo, clasificación, velocidad, frecuencia) para estudios urbanos depende frecuentemente de sensores invasivos costosos (lazos magnéticos, radares) o de inspecciones manuales. Los sistemas basados en video convencional carecían de mecanismos robustos para manejar oclusiones y evitar duplicidad de conteo sin calibraciones complejas de cámara.

**Motivación:** Desarrollar una solución no invasiva y económica capaz de reutilizar cámaras de videovigilancia estándar (CCTV) o tomas laterales no calibradas para generar datos viales estructurados de manera automatizada.

**Objetivo:** Diseñar e implementar un sistema de visión artificial y aprendizaje profundo para la detección, clasificación, seguimiento y conteo de vehículos en tiempo real a partir de secuencias de video en escenarios no controlados, exportando los resultados a un formato estructurado.

### Aportación personal

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

Mario es el autor de la tesis de maestría. Diseñó la arquitectura modular del sistema, recolectó y etiquetó manualmente el dataset de 21,000 imágenes en 7 clases usando LabelImg, entrenó y optimizó los modelos YOLOv3 en DarkNet/TensorFlow, e integró el flujo de seguimiento y conteo vehicular con filtro de Kalman y manejo de oclusiones.

### Metodología

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

  Carga de video (MP4/MOV) $\rightarrow$ Extracción de fotogramas $\rightarrow$ Detección y clasificación multiclase con YOLOv3 $\rightarrow$ Seguimiento temporal y asociación de datos con AutoTrack (Filtro de Kalman + Algoritmo Húngaro) $\rightarrow$ Lógica de gestión de oclusiones y reaparición de objetos $\rightarrow$ Conteo y cálculo de tiempos/distancias $\rightarrow$ Exportación de reporte a archivo CSV.

### Modelos y algoritmos utilizados

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

  - *Detección y clasificación:* Red neuronal convolucional YOLOv3 (arquitectura Darknet-53).
  - *Seguimiento y estimación de trayectoria:* Filtro de Kalman (predicción de estado de movimiento) combinado con el Algoritmo Húngaro para la asignación de identificadores únicos ($ID$).
  - *Manejo de excepciones:* Algoritmo de persistencia de $ID$ para reidentificar vehículos tras oclusiones temporales por otros objetos o infraestructura.

### Software, lenguajes, bibliotecas y hardware

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

  - *Lenguajes y bibliotecas:* Python, TensorFlow, OpenCV, AutoTrack, LabelImg.
  - *Entorno y despliegue:* Linux / Ubuntu, Docker, NVIDIA Docker, Git/GitHub.
  - *Hardware de entrenamiento y prueba:* CPU Intel i7 (8.ª generación), 32 GB RAM y 2 GPU NVIDIA GeForce RTX 2080 Ti (11 GB VRAM cada una).

### Datos, pruebas y experimentos

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

  - *Dataset personalizado:* 21,000 imágenes anotadas divididas equitativamente en 7 clases (3,000 imágenes por clase): Auto, Camioneta, Autobús, Van, Motocicleta, Bicicleta y Persona. Partición: 70 % entrenamiento (14,000 imágenes), 30 % pruebas/validación (7,000 imágenes).
  - *Experimentos de hiperparámetros:* Evaluación de 5 configuraciones de entrenamiento variando resolución de entrada ($416 \times 416$ a $768 \times 768$), tamaño de lote (*Batch* 16 a 64), épocas (14,000 a 18,000) y tiempo de entrenamiento (8 h a 36 h).

### Resultados y métricas verificables

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

  - *Precisión promedio global (Darknet mAP):* Evolución de 25.62 % (Configuración 1) a 90.62 % (Configuración 5 final).
  - *Precisión de clasificación por clase (Configuración 5):* Van: 95.43 %, Camioneta: 93.22 %, Autobús: 93.22 %, Motocicleta: 92.39 %, Bicicleta: 87.92 %, Persona: 85.09 %, Auto: 84.16 %.
  - *Rendimiento computacional:* Tiempo de procesamiento de 1.5 segundos por cada 1.0 segundo de video en el equipo de prueba.
  - *Salida:* Exportación automatizada de archivo CSV con ID, clase, distancia recorrida, tiempo de permanencia y frecuencia vehicular.

### Decisiones técnicas relevantes

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

  - Selección de YOLOv3 sobre métodos tradicionales de sustracción de fondo o clasificadores Haar para mantener robustez ante cambios de iluminación urbana.
  - Incremento del tamaño de resolución a $768 \times 768$ e incremento de lote a 64 en la quinta configuración, lo que elevó la precisión promedio de 59.45 % a 90.62 %.
  - Integración del Filtro de Kalman con AutoTrack para evitar la necesidad de calibración física previa de la lente o perspectiva de la cámara.

### Dificultades y limitaciones

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

**Dificultades encontradas:**

  - Oclusiones severas entre vehículos en vías de alto flujo cuando la cámara se ubica a baja altura lateral.
  - Elevado costo computacional y tiempo de entrenamiento (hasta 36 horas continuas) al aumentar la resolución a $768 \times 768$ px.

**Limitaciones:**

  - Sensibilidad a la posición y ángulo de inclinación de la cámara si la oclusión es prolongada.
  - Velocidad de procesamiento ligeramente superior al tiempo real (1.5s por segundo de video) en el entorno evaluado.

### Aprendizajes y relaciones

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

**Aprendizajes:**

  - El balanceo riguroso de clases y la calidad del etiquetado manual influyen directamente en la reducción de falsos positivos en visión por computadora.
  - Ajustar hiperparámetros clave (resolución de fotograma y tamaño de lote) ofrece retornos significativos en precisión a costa de tiempo de cómputo.
  - El uso de contenedores Docker con soporte GPU garantiza la reproducibilidad de entornos de experimentación en deep learning.

**Publicaciones o proyectos relacionados:** `PUB-01`, `PJT-02`.

### Preguntas profesionales respaldadas

> Contexto de recuperación: Investigación de maestría · Fuente principal: `[SRC-MSC-THESIS-01]`

  - ¿Tiene experiencia construyendo pipelines de visión artificial para procesamiento de video y seguimiento de objetos?
  - ¿Cómo ha realizado el curado, etiquetado y balanceo de datasets propios desde cero?
  - ¿Ha trabajado con YOLO, OpenCV, Filtro de Kalman y contenedores Docker en Linux?
  - ¿Cómo aborda el análisis de fallos e hiperparámetros en redes convolucionales?
