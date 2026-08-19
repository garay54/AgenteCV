# Publicaciones científicas seleccionadas

Este documento detalla las publicaciones científicas proporcionadas en el corpus. La información se sustenta estrictamente en la evidencia de las fuentes primarias y en las declaraciones formales de autoría (CRediT cuando está disponible). `[SRC-PUB-SPEED-2022]` `[SRC-PUB-POTHOLE-2025-ES]` `[SRC-PUB-POTHOLE-2025-EN]`

---

## Nota sobre indexación e idoneidad (JCR)

Las fuentes confirman la publicación de tres artículos científicos revisados por pares. Mario indicó que se encuentran publicados en revistas indexadas en el Journal Citation Reports (JCR), pero las fuentes disponibles no acreditan los cuartiles específicos ni los factores de impacto correspondientes a cada año. El agente puede describirlas como publicaciones científicas arbitradas, pero no debe asignarles un cuartil o factor de impacto sin evidencia adicional. `[SRC-PUB-SPEED-2022]` `[SRC-PUB-POTHOLE-2025-ES]` `[SRC-PUB-POTHOLE-2025-EN]`

---

## PUB-01 — Estimación de velocidad vehicular en tiempo real basada en YOLO

- **Nombres de búsqueda y alias:** artículo de *Applied Sciences* de 2022, artículo de estimación de velocidad, publicación 2907 y *Analysis of Statistical and Artificial Intelligence Algorithms for Real-Time Speed Estimation*.
- **Resumen directo:** El artículo de *Applied Sciences* compara algoritmos estadísticos y de inteligencia artificial para estimar velocidad vehicular en tiempo real a partir de detección YOLOv3 y seguimiento con filtro de Kalman. `[SRC-PUB-SPEED-2022]`
- **Contribución individual documentada de Mario:** Redacción del borrador original y revisión/edición; la declaración CRediT no le atribuye individualmente software o metodología. `[SRC-PUB-SPEED-2022]`
- **Título:** *Analysis of Statistical and Artificial Intelligence Algorithms for Real-Time Speed Estimation Based on Vehicle Detection with YOLO*.
- **Año:** 2022 (Publicado el 11 de marzo de 2022).
- **Revista o medio:** *Applied Sciences* (vol. 12, núm. 6, art. 2907).
- **Estado de publicación:** Publicado (Acceso abierto, Licencia CC BY 4.0).
- **Referencia bibliográfica:** Rodríguez-Rangel, H.; Morales-Rosales, L. A.; Imperial-Rojo, R.; Roman-Garay, M. A.; Peralta-Peñuñuri, G. E.; Lobato-Báez, M. *Analysis of Statistical and Artificial Intelligence Algorithms for Real-Time Speed Estimation Based on Vehicle Detection with YOLO*. Applied Sciences, 2022, 12(6), 2907.
- **Problema abordado:** Evaluar comparativamente el desempeño y la complejidad computacional de algoritmos estadísticos de regresión frente a modelos de inteligencia artificial para la estimación de velocidad vehicular en tiempo real a partir de secuencias de video monoculares no calibradas.
- **Condición de autoría:** Coautor. Su nombre aparece en la cuarta posición de la portada del artículo.
- **Aportación personal:** De acuerdo con la declaración formal CRediT del artículo, Mario participó en la redacción del borrador original (*Writing – original draft*) y en la revisión y edición del manuscrito (*Writing – review & editing*). El documento señala en su nota inicial que todos los autores contribuyeron por igual al trabajo; la declaración CRediT no le atribuye de forma individual exclusiva la autoría del código, el muestreo o la metodología.
- **Participación en colaboración:** Artículo con seis autores en total. Mario colaboró con H. Rodríguez-Rangel, L. A. Morales-Rosales, R. Imperial-Rojo, G. E. Peralta-Peñuñuri y M. Lobato-Báez.
- **Metodología:**
  1. Extracción de secuencias de video monoculares (29 videos procesados, 532 muestras válidas).
  2. Detección vehicular con YOLOv3 y seguimiento de trayectoria con filtro de Kalman para extraer distancias y tiempos.
  3. Entrenamiento y evaluación comparativa de 8 métodos predictivos de velocidad (5 regresiones estadísticas y 3 modelos de machine learning / deep learning).
- **Tecnologías utilizadas:** Python, TensorFlow, scikit-learn, OpenCV, YOLOv3, Filtro de Kalman.
- **Resultados principales:**
  - Los métodos estadísticos simples superaron en precisión y simplicidad computacional a los algoritmos de machine learning evaluados.
  - La regresión lineal estándar obtuvo la mayor precisión con un Error Absoluto Medio (MAE) de 1.694 km/h en el carril central y 0.956 km/h en el último carril. Estos valores proceden del resumen y las tablas principales; la conclusión del artículo invierte puntualmente las etiquetas de los carriles, por lo que no debe utilizarse para asignar esas dos cifras.
- **Relación con tesis, proyectos o experiencia profesional:** Se relaciona con la tesis de maestría (`PJT-02`), consolidando la línea de investigación sobre extracción de métricas viales a partir de video monocular.
- **Enlace público / DOI:** DOI: [https://doi.org/10.3390/app12062907](https://doi.org/10.3390/app12062907).
- **Referencia interna al documento fuente:** `[SRC-PUB-SPEED-2022]`

---

## PUB-02 — Detección inteligente de baches y estimación de profundidad con YOLOv8 y RealSense

- **Nombres de búsqueda y alias:** artículo de *CIENCIA ergo-sum*, artículo en español sobre baches, publicación e37 y *Detección inteligente de baches y estimación de su profundidad*.
- **Resumen directo:** El artículo de *CIENCIA ergo-sum* utiliza YOLOv8 y una cámara Intel RealSense D435i para detectar baches y estimar su profundidad. `[SRC-PUB-POTHOLE-2025-ES]`
- **Contribución individual documentada de Mario:** Es primer autor; como la fuente no contiene una declaración CRediT individual, no deben atribuirse exclusivamente a Mario todas las tareas del equipo. `[SRC-PUB-POTHOLE-2025-ES]`
- **Título:** *Detección inteligente de baches y estimación de su profundidad con aprendizaje profundo para la conservación de carreteras*.
- **Año:** 2025.
- **Revista o medio:** *CIENCIA ergo-sum* (vol. 32, núm. 1, e37).
- **Estado de publicación:** Publicado (Postprint / Versión final de autor, Licencia CC BY-NC-ND 4.0).
- **Referencia bibliográfica:** Román-Garay, M. A.; Hernández-Beltrán, C. A.; Morales-Rosales, L.; Rodríguez-Rangel, H.; Villa-Camacho, M. A.; Soto-Audelo, J. A.; Lepej, P. *Detección inteligente de baches y estimación de su profundidad con aprendizaje profundo para la conservación de carreteras*. CIENCIA ergo-sum, 2025, 32(1), e37.
- **Problema abordado:** Detectar baches en pavimentos e integrar la medición cuantitativa de su profundidad utilizando sensores de bajo costo para superar la falta de datos tridimensionales en inspecciones 2D convencionales.
- **Condición de autoría:** Primer autor. Su nombre aparece al inicio de la portada del artículo.
- **Aportación personal:** La fuente no incluye una declaración CRediT individual explícita; por tanto, las tareas ejecutadas por el equipo de investigación no deben atribuirse en su totalidad a Mario de forma individual. Sólo puede afirmarse con certeza su condición de primer autor y la participación general documentada en el artículo.
- **Participación en colaboración:** Artículo con siete autores en total. Mario colaboró con C. A. Hernández-Beltrán, L. Morales-Rosales, H. Rodríguez-Rangel, M. A. Villa-Camacho, J. A. Soto-Audelo y P. Lepej.
- **Metodología:**
  1. Detección y localización de baches mediante la arquitectura YOLOv8.
  2. Adquisición de mapas de profundidad y nubes de puntos con la cámara RGB-D Intel RealSense D435i.
  3. Procesamiento de la información tridimensional en la región detectada para estimar la profundidad máxima de la cavidad.
- **Tecnologías utilizadas:** Python, PyTorch, YOLOv8, Intel RealSense D435i, OpenCV, bibliotecas de procesamiento 3D.
- **Resultados principales:**
  - *Detección (YOLOv8 sobre 273 imágenes: 173 entrenamiento, 50 validación, 50 prueba):* mAP = 84.7 %, Precisión = 85.7 %, Recall = 76.3 %.
  - *Estimación de profundidad:* Error promedio de 5 mm en una muestra de 7 cavidades comparadas con mediciones manuales de regla/calibrador.
- **Relación con tesis, proyectos o experiencia profesional:** Es una publicación derivada de la investigación doctoral (`PJT-01`), enfocada en la detección rápida y estimación inicial de profundidad.
- **Enlace público / DOI:** DOI: [https://doi.org/10.30878/ces.v32n0a37](https://doi.org/10.30878/ces.v32n0a37).
- **Referencia interna al documento fuente:** `[SRC-PUB-POTHOLE-2025-ES]`

---

## PUB-03 — Arquitectura de evaluación de baches con SegFormer, nubes de puntos y lógica difusa

- **Nombres de búsqueda y alias:** artículo de *Case Studies*, artículo de *Case Studies in Construction Materials*, publicación e04440 y *Architecture for pavement pothole evaluation*.
- **Resumen directo:** El artículo de *Case Studies in Construction Materials* presenta una arquitectura para evaluar baches mediante SegFormer, integración de información 2D/3D y un sistema de lógica difusa para severidad y recomendaciones de mantenimiento. `[SRC-PUB-POTHOLE-2025-EN]`
- **Contribuciones CRediT de Mario:** Conceptualización, investigación, metodología, software y redacción del borrador original. `[SRC-PUB-POTHOLE-2025-EN]`
- **Título:** *Architecture for pavement pothole evaluation using deep learning, machine vision, and fuzzy logic*.
- **Año:** 2025 (Publicado en 2025, e04440).
- **Revista o medio:** *Case Studies in Construction Materials* (vol. 22, e04440).
- **Estado de publicación:** Publicado (Acceso abierto, Licencia CC BY-NC-ND 4.0).
- **Referencia bibliográfica:** Roman-Garay, M.; Rodriguez-Rangel, H.; Hernández-Beltrán, C.; Lepej, P.; Arreygue-Rocha, J. E.; Morales-Rosales, L. A. *Architecture for pavement pothole evaluation using deep learning, machine vision, and fuzzy logic*. Case Studies in Construction Materials, 2025, 22, e04440.
- **Problema abordado:** Desarrollar un sistema integral que combine segmentación semántica precisa de cavidades de baches, proyección geométrica 3D y evaluación de severidad para automatizar las recomendaciones de mantenimiento de pavimentos.
- **Condición de autoría:** Primer autor. Su nombre aparece al inicio de la portada del artículo.
- **Aportación personal:** De acuerdo con la declaración formal CRediT del artículo, Mario participó en: Conceptualización (*Conceptualization*), Investigación (*Investigation*), Metodología (*Methodology*), Software (*Software*) y Redacción del borrador original (*Writing – original draft*).
- **Participación en colaboración:** Artículo con seis autores en total. Mario colaboró con H. Rodriguez-Rangel, C. Hernández-Beltrán, P. Lepej, J. E. Arreygue-Rocha y L. A. Morales-Rosales.
- **Metodología:**
  1. Segmentación semántica 2D del área de baches mediante el modelo Transformer SegFormer.
  2. Integración con datos 3D obtenidos con Intel RealSense D435i para cuantificar diámetro y profundidad.
  3. Evaluación de severidad técnica y generación de recomendaciones de reparación mediante un sistema de inferencia difusa Mamdani, cuyos resultados se compararon utilizando el manual de evaluaciones de la SICT.
- **Tecnologías utilizadas:** Python, PyTorch, SegFormer, Intel RealSense D435i, Open3D y NumPy.
- **Resultados principales:**
  - *Segmentación semántica (SegFormer):* Recall = 90.87 %, Precisión = 90.01 %, F1-score = 90.433 %, IoU = 85.872 %.
  - *Estimación de profundidad:* El artículo menciona valores de error como 5.94 mm, aproximadamente 6 mm y 7.82 mm en distintas secciones o subconjuntos. Estas cifras no deben combinarse. Para la evaluación homogénea final de 11 muestras de campo deben utilizarse los valores del documento doctoral `[SRC-PHD-THESIS-01]`.
- **Relación con tesis, proyectos o experiencia profesional:** Es la publicación principal del módulo de baches de la investigación doctoral (`PJT-01` / `SRC-PHD-THESIS-01`).
- **Enlace público / DOI:** DOI: [https://doi.org/10.1016/j.cscm.2025.e04440](https://doi.org/10.1016/j.cscm.2025.e04440).
- **Referencia interna al documento fuente:** `[SRC-PUB-POTHOLE-2025-EN]`
