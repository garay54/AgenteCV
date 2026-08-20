# Preguntas frecuentes sobre la trayectoria

## Guía de uso

Las respuestas están redactadas en primera persona para una interacción conversacional profesional. Cada respuesta cuenta con un estado de validación:

- **Validada:** Sustentada directamente en datos explícitos de las fuentes.
- **Validada con restricción:** Sustentada en fuentes, pero con límites explícitos o datos relacionados pendientes de confirmar.
- **Revisar con Mario:** Interpretación razonable basada en evidencia que requiere validación personal.
- **Pendiente:** Ausencia de datos en el corpus; el agente no debe inventar ni improvisar.

---

## ¿Cómo resumirías tu perfil profesional?

**Estado: Validada**

Soy Ingeniero Mecatrónico, Maestro en Ciencias de la Computación y Doctor en Ciencias de la Computación. Cuento con más de cuatro años de experiencia en investigación de posgrado en visión por computadora, aprendizaje profundo y procesamiento de datos. Mi trabajo se centra en construir pipelines de extremo a extremo que integran modelos de segmentación semántica (Transformers y CNNs), procesamiento geométrico 2D/3D y sistemas de inferencia difusa para apoyar la toma de decisiones. Asimismo, cuento con conocimientos prácticos y conceptuales en IA generativa, RAG e ingeniería de prompts. `[SRC-CV-01]` `[SRC-PHD-THESIS-01]` `[SRC-USER-CONFIRM-2026-08-18]`

---

## ¿Cuál es tu formación académica?

**Estado: Validada**

Tengo tres grados académicos en ingeniería y posgrado:
1. **Doctorado en Ciencias de la Computación:** Grado obtenido por el Tecnológico Nacional de México, campus Culiacán, tras la defensa de tesis realizada el 10 de agosto de 2026.
2. **Maestría en Ciencias de la Computación:** Grado obtenido en agosto de 2022 por el Tecnológico Nacional de México, campus Culiacán.
3. **Ingeniería Mecatrónica:** Título obtenido en 2019 por el Tecnológico Nacional de México, con reconocimiento por desempeño sobresaliente en el examen CENEVAL EGEL. `[SRC-CV-01]` `[SRC-MSC-THESIS-01]` `[SRC-PHD-THESIS-01]` `[SRC-USER-CONFIRM-2026-08-18]`

---

## ¿Cuál consideras tu principal contribución de investigación?

**Estado: Validada**

Mi principal contribución es el desarrollo de un mecanismo inteligente de extremo a extremo para la auscultación automatizada de pavimentos flexibles. En lugar de limitarme a detectar daños visualmente, logré integrar la segmentación semántica mediante modelos Transformers (SegFormer) y redes U-Net con la cuantificación física tridimensional y bidimensional (diámetro, profundidad, anchura, longitud), conectando esas mediciones con sistemas difusos calibrados según las normas técnicas de la SICT para emitir recomendaciones directas de mantenimiento. `[SRC-PHD-THESIS-01]` *(Detalles en `knowledge/research.md`)*.

---

## ¿Qué retos técnicos enfrentaste en la medición física de deterioros?

**Estado: Validada**

Uno de los mayores retos fue la variabilidad física y las limitaciones de los sensores en campo. Para baches volumétricos, fue necesario alinear mapas de profundidad y nubes de puntos 3D mediante RANSAC para aislar la cavidad del plano del pavimento. Para grietas, los sensores 3D no ofrecían resolución milimétrica, por lo que diseñé una tubería geométrica 2D basada en esqueletización, Análisis de Componentes Principales (PCA) para orientación local y trazado de rayos subpíxel. Esto demostró que la modalidad sensorial debe adaptarse a la geometría específica del problema. `[SRC-PHD-THESIS-01]` *(Detalles en `knowledge/research.md`)*.

---

## ¿Cómo evalúas y validas tus modelos de machine learning?

**Estado: Validada**

Utilizo un enfoque riguroso y multidimensional según la tarea:
- **Segmentación semántica:** IoU, Dice global *out-of-fold*, Precisión, Recall y F1-score.
- **Cuantificación física:** Error Absoluto Medio (MAE) y Error Cuadrático Medio (RMSE) comparados directamente contra mediciones manuales de referencia tomadas en campo.
- **Evaluación de fuga de datos:** Partición de conjuntos mediante *Grouped 5-Fold Cross-Validation* a nivel de secuencia de video para evitar sobreajuste temporal.
- **Explicabilidad visual:** Mapas de atención Grad-CAM evaluados con métricas CAM-IoU y ROAD. `[SRC-PHD-THESIS-01]`

---

## ¿Qué publicaciones científicas respaldan tu trayectoria?

**Estado: Validada**

Cuento con tres publicaciones científicas principales en revistas arbitradas:
1. **Applied Sciences (2022):** Estudio comparativo de algoritmos estadísticos y de IA para estimación de velocidad vehicular en tiempo real (`PUB-01`). DOI: 10.3390/app12062907.
2. **CIENCIA ergo-sum (2025):** Detección inteligente de baches y estimación de profundidad con YOLOv8 y cámaras RGB-D (`PUB-02`). DOI: 10.30878/ces.v32n0a37.
3. **Case Studies in Construction Materials (2025):** Arquitectura de evaluación de baches combinando SegFormer, nubes 3D y lógica difusa (`PUB-03`). DOI: 10.1016/j.cscm.2025.e04440.
*(Detalles y declaraciones CRediT en `knowledge/publications.md`)*.

---

## ¿Cuál es tu experiencia práctica con IA Generativa y RAG?

**Estado: Validada con restricción**

Cuento con formación y conocimientos prácticos declarados en arquitectura de sistemas RAG (ingestión, fragmentación o *chunking*, embeddings, búsqueda vectorial, recuperación y reranking), ingeniería de prompts, manejo de contexto, respuestas estructuradas y flujos agénticos (conceptos de LangChain y MCP). No obstante, mis publicaciones y tesis se centran en visión artificial y aprendizaje profundo; las fuentes actuales no demuestran un proyecto comercial o sistema productivo desplegado de IA generativa. `[SRC-CV-01]`

---

## ¿Tienes experiencia en docencia o asesoría técnica?

**Estado: Validada con alcance limitado**

He colaborado como asesor de proyectos y tesis de licenciatura en el Tecnológico Nacional de México, guiando a estudiantes en programación en Python, preparación y etiquetado de datasets, entrenamiento de modelos, evaluación de métricas y redacción de documentación técnica. Esta experiencia debe describirse como una actividad académica vinculada al posgrado; las fuentes no demuestran que haya sido una plaza docente o empleo empresarial formal. `[SRC-CV-01]`

---

## ¿Cuál ha sido una lección clave al comparar modelos simples y complejos?

**Estado: Validada**

En nuestro estudio de estimación de velocidad vehicular (`PUB-01`), los modelos de regresión estadística simple superaron en precisión y simplicidad computacional a algoritmos más complejos como Random Forest, SVM o redes neuronales MLP. Esta experiencia me enseñó la importancia fundamental de establecer y medir líneas base simples antes de incrementar la complejidad de una solución de IA. `[SRC-PUB-SPEED-2022]`

---

## ¿Qué motivaciones o aspectos personales puedes compartir para una entrevista laboral?

**Estado: Pendiente / Revisar con Mario**

Las fuentes de archivo proporcionan evidencia técnica de investigación, pero no contienen episodios narrativos sobre fracasos personales, situaciones de conflicto o liderazgo ni motivaciones específicas para una organización cliente. El agente debe indicar que no dispone de esa información y no debe inventar una historia personal.
