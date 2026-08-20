# Proyectos seleccionados

## PJT-01 — Mecanismo inteligente para evaluar baches y grietas en pavimentos flexibles

### Contexto
Proyecto de investigación doctoral (2022-2026) orientado a automatizar la auscultación e inspección de pavimentos flexibles. El objetivo fue integrar detección, cuantificación física tridimensional/bidimensional, evaluación de severidad y recomendaciones de mantenimiento dentro de un flujo trazable. `[SRC-PHD-THESIS-01]`

### Problema
Las inspecciones manuales consumen tiempo, exponen al personal al tráfico vehicular y presentan alta subjetividad. Detectar un deterioro en imagen 2D no es suficiente: para fundamentar acciones de conservación de carreteras se requieren dimensiones físicas reales (diámetro, profundidad, anchura, longitud) y su encuadre en normas técnicas.

### Responsabilidad documentada
Mario desarrolló este trabajo como autor de la tesis doctoral. Diseñó la arquitectura de los dos módulos principales (baches y grietas), construyó los conjuntos de datos, desarrolló la tubería de integración 2D/3D con nubes de puntos y RANSAC, la canalización de esqueletización, PCA y trazado de rayos subpíxel para grietas, implementó la optimización con Optuna, las pruebas de explicabilidad (Grad-CAM/CAM-IoU/ROAD) y la formulación de los sistemas difusos. `[SRC-PHD-THESIS-01]`

### Arquitectura funcional
1. Adquisición de datos con cámara RGB-D Intel RealSense D435i y GoPro HERO8 Black.
2. Segmentación semántica especializada: SegFormer para baches y U-Net con MiT-B2 para grietas (pérdida Dice-BCE).
3. Cuantificación geométrica: proyección de máscaras sobre nubes de puntos 3D para baches (diámetro y profundidad) y esqueletización con PCA para grietas (anchura y longitud).
4. Seguimiento temporal de grietas entre fotogramas mediante el algoritmo SORT.
5. Evaluación de explicabilidad con Grad-CAM, CAM-IoU y ROAD.
6. Sistemas de Inferencia Difusa (FIS Mamdani) jerárquicos alineados con criterios de la SICT.

### Tecnologías y métodos
Python, PyTorch, CUDA, SegFormer, U-Net, MiT-B2, Optuna, RANSAC, SORT, PCA, Grad-CAM, Intel RealSense D435i, GoPro HERO8 Black, 2 GPU NVIDIA GeForce RTX 4070 Ti, Nubes de puntos 3D, Lógica Difusa.

### Resultados
- *Baches:* IoU de segmentación de 85.87 %; MAE de diámetro de 3.73 cm y MAE de profundidad de 7.02 mm (RMSE 7.91 mm) evaluados en 11 muestras de campo.
- *Grietas:* Dice global *out-of-fold* de 0.7415; error relativo medio de 24.15 % en anchura y 36.31 % en longitud.
- *Sistema difuso:* Sus resultados se compararon utilizando el manual de evaluaciones de la SICT.
*(Para el detalle metodológico completo, véase `knowledge/research.md`).* `[SRC-PHD-THESIS-01]`

---

## PJT-02 — Sistema generador de información vial a partir de secuencia de imágenes

### Contexto
Proyecto de tesis de maestría (2020-2022) concluido en el Tecnológico Nacional de México, campus Culiacán. Su objetivo fue aprovechar secuencias de video monoculares para extraer datos de tránsito sin requerir sensores invasivos en la vía. `[SRC-MSC-THESIS-01]`

### Problema
Los estudios de ingeniería de tránsito requieren recolectar aforos, clasificaciones vehiculares, velocidades y frecuencias. Los sensores tradicionales de carretera implican costos altos e interrupción de la circulación, mientras que los sistemas basados en video convencional suelen duplicar conteos ante oclusiones.

### Responsabilidad documentada
Mario diseñó y desarrolló el sistema como autor de la tesis de maestría, recolectó y etiquetó el conjunto de datos de 21,000 imágenes, configuró y entrenó los modelos YOLOv3 en DarkNet/TensorFlow, integró la lógica de seguimiento vehicular con Filtro de Kalman y AutoTrack, y ejecutó los experimentos computacionales. `[SRC-MSC-THESIS-01]`

### Arquitectura funcional
1. Carga de secuencias de video (MP4/MOV).
2. Extracción y preprocesamiento de fotogramas.
3. Detección y clasificación multiclase con YOLOv3.
4. Seguimiento vehicular y predicción de trayectoria con Filtro de Kalman y AutoTrack.
5. Gestión de oclusiones temporales y reaparición de objetos mediante persistencia de ID.
6. Conteo y cálculo de tiempos/distancias.
7. Exportación automatizada a reportes CSV.

### Tecnologías
Python, OpenCV, YOLOv3, Darknet, TensorFlow, Filtro de Kalman, Algoritmo Húngaro, AutoTrack, Docker, NVIDIA Docker, Ubuntu Linux, LabelImg y 2 GPU NVIDIA GeForce RTX 2080 Ti.

### Resultados
- Dataset propio de 21,000 imágenes etiquetadas en 7 clases (3,000 por clase).
- Precisión promedio global (mAP) final de 90.62 % en la configuración optimizada.
- Precisión por clase entre 84.16 % (Auto) y 95.43 % (Van).
- Procesamiento de 1.5 segundos por cada segundo de video.
*(Para el detalle metodológico completo, véase `knowledge/research.md`).* `[SRC-MSC-THESIS-01]`

---

## PJT-03 — Análisis comparativo de algoritmos para la estimación de velocidad vehicular en tiempo real

### Contexto
Investigación científica publicada en *Applied Sciences* (2022) centrada en la evaluación empírica de algoritmos estadísticos frente a modelos de inteligencia artificial para la estimación de velocidad vehicular a partir de video. `[SRC-PUB-SPEED-2022]`

### Alcance técnico
- Procesamiento de 29 videos monoculares y 532 muestras válidas de tránsito.
- Detección vehicular mediante YOLOv3 y seguimiento con Filtro de Kalman para alimentar los estimadores de velocidad.
- Evaluación comparativa de 8 métodos: 5 regresiones estadísticas (Regresión Lineal, Ridge, Lasso, Bayesian Ridge, Elastic Net) y 3 modelos de IA (Random Forest, SVM, Red Perceptrón Multicapa - MLP).
- La regresión lineal simple obtuvo la mayor precisión: MAE de 1.694 km/h en el carril central y 0.956 km/h en el último carril.

### Contribución personal verificable
La declaración formal CRediT del artículo atribuye a Mario la redacción del borrador original (*Writing – original draft*) y la revisión/edición (*Writing – review & editing*). Los autores tienen contribución igualitaria acreditada en la nota del manuscrito. `[SRC-PUB-SPEED-2022]`

### Aprendizaje clave
Los modelos estadísticos simples superaron en precisión y eficiencia computacional a las redes neuronales y clasificadores complejos para este problema específico, demostrando la importancia de establecer líneas base simples antes de incrementar la complejidad del modelo. `[SRC-PUB-SPEED-2022]`

---

## PJT-04 — AgenteCV: agente conversacional de currículum con RAG

### Contexto
Proyecto personal de agente conversacional orientado a responder preguntas verificables sobre la experiencia, formación, habilidades, proyectos y publicaciones profesionales de Mario. La plataforma cliente proporciona el chat y consume el endpoint público del agente. `[SRC-PROJECT-AGENTECV-2026]`

### Problema
Un currículum tradicional presenta información estática y obliga al lector a localizar manualmente los datos relevantes. El proyecto transforma una base de conocimiento profesional curada en una experiencia conversacional, manteniendo trazabilidad hacia las fuentes y evitando inventar información ausente.

### Responsabilidad documentada
Mario diseñó y desarrolló la API backend, la preparación del corpus, el proceso de fragmentación, la generación de embeddings, el almacenamiento vectorial, la recuperación RAG, la adaptación al protocolo Open Responses, las pruebas automatizadas y el despliegue. `[SRC-PROJECT-AGENTECV-2026]`

### Arquitectura funcional
1. Una API FastAPI recibe solicitudes autenticadas compatibles con Open Responses.
2. El historial recibido se normaliza y se procesa sin almacenar sesiones conversacionales.
3. La consulta se convierte en un embedding y recupera fragmentos desde ChromaDB.
4. Un reranking combina similitud vectorial, diversidad documental y coincidencia léxica.
5. El contexto recuperado fundamenta la generación de la respuesta mediante OpenAI.
6. El endpoint entrega una respuesta JSON completa o una secuencia SSE incremental.

### Tecnologías y métodos
Python, FastAPI, Pydantic, OpenAI Responses API, OpenAI Embeddings, ChromaDB, RAG, búsqueda vectorial, reranking híbrido, Server-Sent Events, Pytest y Railway.

### Estado y resultados
- API desplegada mediante HTTPS con autenticación Bearer, límites de entrada, rate limiting y cabeceras defensivas.
- Recuperación evaluada de forma reproducible sobre el banco de preguntas del proyecto.
- Respuestas completas y streaming SSE implementados y validados desde el cliente conversacional.
- Suite automatizada de 56 pruebas para contrato, autenticación, límites HTTP, RAG, generación y streaming. `[SRC-PROJECT-AGENTECV-2026]`

---

## PJT-05 — RankVideo: editor de videos de ranking TOP N

### Contexto
Proyecto personal de aplicación de escritorio para producir videos de ranking TOP N mediante proyectos reutilizables, edición de línea de tiempo, textos superpuestos, importación de contenido multimedia y exportación con FFmpeg. `[SRC-PROJECT-RANKVIDEO-2026]`

### Problema
La producción de videos de ranking requiere coordinar posiciones, recursos multimedia, duración, textos y exportación. RankVideo reúne estas operaciones en un flujo visual reutilizable para reducir la edición manual repetitiva.

### Responsabilidad documentada
Mario desarrolló el prototipo y su arquitectura de escritorio, integrando la interfaz de edición, el estado compartido de la aplicación, el manejo local de recursos multimedia y el proceso de exportación. `[SRC-PROJECT-RANKVIDEO-2026]`

### Arquitectura funcional
1. Electron proporciona el contenedor de escritorio y el acceso a capacidades locales.
2. React implementa la interfaz y los editores de ranking, línea de tiempo, proyectos y textos.
3. Zustand mantiene el estado compartido de la aplicación.
4. El flujo de trabajo permite importar contenido multimedia local y reutilizar proyectos.
5. FFmpeg procesa la exportación final de video.
6. La configuración de empaquetado contempla Windows, Linux y macOS.

### Tecnologías
Electron, React, TypeScript, Vite, Zustand, Tailwind CSS, FFmpeg, Node.js y npm.

### Estado actual
Prototipo funcional en desarrollo activo. El repositorio conserva el código fuente y excluye deliberadamente los builds e instaladores generados. `[SRC-PROJECT-RANKVIDEO-2026]`
