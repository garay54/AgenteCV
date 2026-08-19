# Habilidades y evidencia técnica

## Escala de evaluación de evidencia

- **Demostrada:** Existe un proyecto de tesis, publicación o experimento con metodología y métricas verificables en las fuentes.
- **Aplicada:** Existe uso explícito documentado en repositorios o metodologías, pero la evidencia no detalla experimentos de comparación individual.
- **Declarada:** Aparece listada en el CV, sin un proyecto o reporte técnico detallado entre las fuentes de archivo revisadas.
- **Conceptual / Familiaridad:** La fuente describe conocimiento teórico o familiaridad práctica, sin un sistema productivo desplegado.

---

## 1. Programación y manejo de datos

| Habilidad | Nivel de evidencia | Evidencia y fuente | Último uso documentado |
|---|---|---|---|
| Python | Demostrada | Pipelines de extremo a extremo en tesis de maestría y doctorado: visión artificial, PyTorch, TensorFlow, geometría 3D, Optuna y lógica difusa. | 2026 `[SRC-PHD-THESIS-01]` |
| PyTorch | Demostrada | Segmentación semántica de grietas y baches con U-Net/MiT-B2 y SegFormer, funciones de pérdida compuestas (Dice-BCE), optimización Optuna (PyTorch 2.9.1, CUDA 12.8). | 2026 `[SRC-PHD-THESIS-01]` |
| TensorFlow / DarkNet | Demostrada | Entrenamiento de modelos de detección YOLOv3 en maestría y red MLP en estudio de velocidad. | 2022 `[SRC-MSC-THESIS-01]` `[SRC-PUB-SPEED-2022]` |
| Scikit-learn | Aplicada | Modelado de regresión estadística, SVM y Random Forest para estimación de velocidad. | 2022 `[SRC-PUB-SPEED-2022]` |
| NumPy y pandas | Aplicada | Procesamiento numérico, manipulación de matrices de datos 2D/3D y generación de expedientes CSV. | 2026 `[SRC-PHD-THESIS-01]` |
| SQL | Declarada | Listada en el CV; no se incluye un proyecto o consulta de base de datos específica en las fuentes. | Fecha no documentada `[SRC-CV-01]` |
| JavaScript y HTML/CSS | Declarada | Listadas en el CV; no se incluye un proyecto web o frontend específico en las fuentes de archivo. | Fecha no documentada `[SRC-CV-01]` |
| JSON y Validación | Declarada | Listada en el CV; utilizada en estructuración de anotaciones y configuraciones de experimentos. | 2026 `[SRC-CV-01]` |

---

## 2. Machine Learning y Aprendizaje Profundo

| Habilidad | Nivel de evidencia | Evidencia y fuente | Último uso documentado |
|---|---|---|---|
| Segmentación Semántica (Transformers & CNNs) | Demostrada | SegFormer para baches y U-Net con codificador MiT-B2 preentrenado para grietas. | 2026 `[SRC-PHD-THESIS-01]` |
| Detección de Objetos (YOLO) | Demostrada | YOLOv3 (maestría, 7 clases viales) y YOLOv8 (detección de baches). | 2025 `[SRC-MSC-THESIS-01]` `[SRC-PUB-POTHOLE-2025-ES]` |
| Transfer Learning | Demostrada | Ajuste fino de codificadores preentrenados (MiT-B2 en ImageNet) y pesos de YOLO. | 2026 `[SRC-PHD-THESIS-01]` |
| Optimización de Hiperparámetros (Optuna) | Demostrada | Búsqueda automatizada sobre 20 configuraciones de arquitectura, codificadores y funciones de pérdida. | 2026 `[SRC-PHD-THESIS-01]` |
| Evaluación y Métricas de Modelos | Demostrada | Evaluación con IoU, Dice global out-of-fold, Precisión, Recall, F1-score, MAE, RMSE y matrices de confusión. | 2026 `[SRC-PHD-THESIS-01]` |
| Diseño de Experimentos y Partición | Demostrada | Partición de datos mediante *Grouped 5-Fold Cross-Validation* para evitar fuga temporal entre secuencias. | 2026 `[SRC-PHD-THESIS-01]` |
| Análisis de Casos de Fallo | Demostrada | Evaluación cualitativa y cuantitativa de errores por iluminación, sombras, oclusiones y ruido sensorial. | 2026 `[SRC-PHD-THESIS-01]` |

---

## 3. Visión por Computadora, Datos Espaciales y Explicabilidad

| Habilidad | Nivel de evidencia | Evidencia y fuente | Último uso documentado |
|---|---|---|---|
| Nubes de Puntos y RGB-D | Demostrada | Fusión de imágenes RGB con mapas de profundidad de Intel RealSense D435i y nubes 3D para medir cavidades. | 2026 `[SRC-PHD-THESIS-01]` |
| Geometría 3D y RANSAC | Demostrada | Estimación de plano de pavimento con RANSAC y proyección 2D-to-3D para medir profundidad y diámetro. | 2026 `[SRC-PHD-THESIS-01]` |
| Procesamiento Geométrico 2D | Demostrada | Esqueletización morfológica, PCA para orientación local y trazado de rayos subpíxel para medir anchura/longitud de grietas. | 2026 `[SRC-PHD-THESIS-01]` |
| Seguimiento de Objetos (Tracking) | Demostrada | Algoritmo AutoTrack / Filtro de Kalman + Húngaro (maestría) y algoritmo SORT para grietas (doctorado). | 2026 `[SRC-MSC-THESIS-01]` `[SRC-PHD-THESIS-01]` |
| OpenCV | Demostrada | Preprocesamiento de video, redimensionamiento, máscaras, transformaciones morfológicas y anotaciones. | 2026 `[SRC-PHD-THESIS-01]` |
| Inteligencia Artificial Explicable (XAI) | Demostrada | Generación de mapas de atención Grad-CAM y evaluación con métricas CAM-IoU y ROAD. | 2026 `[SRC-PHD-THESIS-01]` |
| Sistemas de Inferencia Difusa | Demostrada | Diseño de FIS Mamdani jerárquicos para traducir mediciones físicas en severidad y recomendaciones de reparación SICT. | 2026 `[SRC-PHD-THESIS-01]` |

---

## 4. Ingeniería de Software y Entornos Operativos

| Habilidad | Nivel de evidencia | Evidencia y fuente | Último uso documentado |
|---|---|---|---|
| Linux / Ubuntu | Demostrada | Desarrollo, entrenamiento y evaluación en Ubuntu 20.04 y entornos Linux con GPU. | 2026 `[SRC-MSC-THESIS-01]` `[SRC-PHD-THESIS-01]` |
| Git / GitHub | Aplicada | Control de versiones y repositorios de código/datasets para publicaciones científicas. | 2026 `[SRC-CV-01]` `[SRC-PUB-SPEED-2022]` |
| Docker y NVIDIA Docker | Aplicada | Contenedores para la ejecución reproducible de experimentos deep learning con aceleración GPU. | 2022 `[SRC-MSC-THESIS-01]` |
| Código Modular y Depuración | Aplicada | Desarrollo de componentes desacoplados para adquisición, segmentación, geometría e inferencia. | 2026 `[SRC-PHD-THESIS-01]` |
| APIs REST (FastAPI / Flask) | Declarada / Conceptual | Listadas en el CV como fundamentos; no se incluye una API desplegada en las fuentes de archivo. | Fecha no documentada `[SRC-CV-01]` |
| Prácticas de Testing y Tipado | Declarada | Listadas en el CV; no se adjunta una suite de pruebas unitarias en las fuentes de archivo. | Fecha no documentada `[SRC-CV-01]` |

---

## 5. IA Generativa y Sistemas de Modelos de Lenguaje

| Habilidad | Nivel de evidencia | Acotación de evidencia y respuesta segura |
|---|---|---|
| Aplicaciones con LLM e Ingeniería de Prompts | Conceptual / Familiaridad | Declarada en el CV. No existe evidencia de un sistema comercial o productivo desplegado. `[SRC-CV-01]` |
| Generación Aumentada por Recuperación (RAG) | Conceptual / Familiaridad | Declarada en el CV: limpieza, fragmentación, embeddings, recuperación y reranking. Debe distinguirse formación práctica de despliegue comercial. `[SRC-CV-01]` |
| Embeddings y Búsqueda Vectorial | Conceptual / Familiaridad | Declarada en el CV. Debe presentarse como conocimiento conceptual y práctico en desarrollo. `[SRC-CV-01]` |
| Manejo de Contexto y Respuestas Estructuradas | Conceptual / Familiaridad | Declarada en el CV, sin evidencia de un sistema productivo desplegado. `[SRC-CV-01]` |
| Flujos Agénticos y Tool Calling | Conceptual / Familiaridad | Declarada en el CV: conceptos de flujos agénticos, LangChain y MCP. `[SRC-CV-01]` |
| Seguridad en LLM (OWASP Top 10) | Conceptual / Familiaridad | Declarada en el CV como conocimiento conceptual de seguridad en aplicaciones con LLM. `[SRC-CV-01]` |
