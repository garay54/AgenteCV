# Base de conocimiento profesional

## Propósito

Esta carpeta contiene la versión estructurada, depurada y apta para recuperación de la trayectoria profesional de Mario Alberto Roman Garay. Fue construida a partir del CV, las tesis de maestría y doctorado y tres artículos científicos proporcionados en `FuenteDeVerdad_md/`.

## Archivos

- `profile.md`: identidad profesional, objetivo, educación, idiomas y fortalezas.
- `experience.md`: experiencia académica y de investigación con fechas, responsabilidades y resultados.
- `projects.md`: proyectos explicables de principio a fin.
- `skills.md`: habilidades, nivel de evidencia y última utilización documentada.
- `publications.md`: publicaciones, resultados y contribuciones verificables.
- `research.md`: síntesis curada de las investigaciones de maestría y doctorado.
- `faq.md`: respuestas preparadas para preguntas profesionales frecuentes; se conserva como referencia y apoyo para pruebas, pero no se indexa.
- `question_bank.md`: banco inicial de preguntas para probar recuperación y comportamiento.
- `open_questions.md`: datos ausentes, inconsistentes o pendientes de confirmación.
- `sources/index.md`: catálogo de fuentes y reglas de uso.

## Reglas para el agente

1. Responder únicamente con hechos contenidos en esta carpeta.
2. No revelar ni intentar reconstruir teléfonos, correos electrónicos, direcciones exactas, identificadores personales, firmas o datos familiares.
3. No presentar la actividad de investigación de posgrado como empleo empresarial.
4. Presentar el doctorado como concluido: Mario defendió su tesis y obtuvo el grado el 10 de agosto de 2026, según la confirmación registrada en `[SRC-USER-CONFIRM-2026-08-18]`.
5. No inventar certificaciones, fechas, cargos, métricas, contribuciones de autoría o niveles de dominio.
6. Relacionar cada afirmación cuantitativa con su fuente y con el proyecto o publicación donde fue medida.
7. Cuando dos fuentes difieran, mencionar la discrepancia o utilizar la fuente más reciente indicando su alcance; nunca combinar cifras como si provinieran del mismo experimento.
8. Si la información solicitada no está documentada, responder que no existe evidencia suficiente y ofrecer información relacionada.

## Política para el RAG

Para el MVP sólo se indexarán `profile.md`, `experience.md`, `projects.md`, `skills.md`, `publications.md` y `research.md`.

Quedan excluidos del índice `faq.md`, `question_bank.md`, `open_questions.md`, este README, `sources/index.md` y los documentos originales completos. `faq.md` se utilizará como referencia conversacional y apoyo para pruebas; `question_bank.md` se utilizará para evaluación; `open_questions.md` y `sources/index.md` conservarán trazabilidad interna.

Los originales contienen datos personales, agradecimientos, direcciones editoriales y otras secciones que no son necesarias para responder sobre la trayectoria profesional.

Los artículos o tesis completos sólo deben incorporarse después de aplicar filtros de privacidad, conservar metadatos de procedencia y evaluar la calidad de recuperación.

## Estado de la información

- Última consolidación: 18 de agosto de 2026.
- Idioma principal: español.
- Información sensible omitida deliberadamente.
- Los puntos que requieren intervención de Mario están enumerados en `open_questions.md`.
