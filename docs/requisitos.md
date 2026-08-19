# Requisitos del agente de CV — Reto IA Banorte

## 1. Alcance del documento

Este documento contiene únicamente los requisitos que debe cumplir el agente de CV, su interfaz de integración, su mecanismo RAG y la evaluación de su comportamiento.

Quedan fuera de este documento las decisiones de tecnología, proveedor, modelo, framework, almacenamiento y plataforma de despliegue. Las actividades administrativas y la comunicación con Recursos Humanos quedan fuera, salvo los compromisos explícitos de entrega y operación registrados en la sección 10.

## 2. Fuentes

- **F01 — Instrucciones oficiales del reto:** mensaje recibido del personal de reclutamiento de Banorte.
- **F02 — Indicación recibida en entrevista:** estudiar e incorporar RAG y su evaluación como parte del reto técnico.
- **F03 — Requisitos derivados:** condiciones necesarias para que el agente sea coherente, confiable, seguro, verificable y operable.
- **F04 — Plataforma y agente Guía de Banorte:** el formulario aporta evidencia de integración; el agente Guía aporta orientación general, pero confirmó que no dispone del contrato HTTP exacto.
- **F05 — Decisiones directas de Mario:** elecciones de producto, alcance, entrega y operación confirmadas el 18 de agosto de 2026. No sustituyen requisitos oficiales de Banorte.

## 3. Requisitos funcionales

| ID | Requisito | Fuente | Verificación |
|---|---|---|---|
| FUN-01 | El agente deberá responder preguntas sobre el perfil profesional de Mario. | F01 | Ejecutar preguntas directas y comprobar que las respuestas correspondan a la fuente profesional autorizada. |
| FUN-02 | El agente deberá responder preguntas sobre la formación académica de Mario cuando esa información exista en la fuente autorizada. | F01, F03 | Comparar las respuestas con los registros académicos incluidos en la base de conocimiento. |
| FUN-03 | El agente deberá responder preguntas sobre la experiencia laboral, empresas, puestos, periodos y responsabilidades de Mario. | F01 | Comparar las respuestas con la experiencia documentada. |
| FUN-04 | El agente deberá responder preguntas sobre las habilidades técnicas y profesionales de Mario. | F01 | Comprobar que cada habilidad mencionada se encuentre documentada. |
| FUN-05 | El agente deberá responder preguntas sobre proyectos, participación, tecnologías y resultados verificables de Mario. | F01 | Comparar las respuestas con los proyectos incluidos en la fuente autorizada. |
| FUN-06 | El agente sólo deberá comunicar investigaciones, métricas de impacto o resultados cuantitativos cuando estén respaldados por la información autorizada. | F03 | Probar preguntas sobre métricas existentes e inexistentes y revisar que no se inventen valores. |
| FUN-07 | El agente deberá responder preguntas directas y preguntas de seguimiento relacionadas con la trayectoria profesional. | F01, F03 | Ejecutar conversaciones de varios turnos y verificar continuidad temática. |
| FUN-08 | El agente deberá identificarse como el agente profesional de Mario, utilizar primera persona por defecto al describir su trayectoria y mantener identidad, alcance y tono consistentes sin afirmar que es una persona humana. | F03, F05 | Revisar conversaciones con distintas formulaciones y comprobar que no cambie de identidad, persona gramatical o propósito. |
| FUN-09 | El agente deberá indicar claramente cuando no disponga de información suficiente para responder. | F03 | Formular preguntas sobre información ausente y comprobar que reconozca la limitación. |
| FUN-10 | El agente deberá manejar de forma segura y útil las preguntas fuera del ámbito de la trayectoria profesional. | F03 | Ejecutar preguntas fuera de dominio y verificar que aplique una respuesta de alcance sin inventar información. |
| FUN-11 | El agente no deberá revelar información privada, confidencial o no autorizada. | F03 | Ejecutar solicitudes de información restringida y comprobar que no sea expuesta. |

## 4. Requisitos de conocimiento y RAG

| ID | Requisito | Fuente | Verificación |
|---|---|---|---|
| RAG-01 | El agente deberá incorporar generación aumentada por recuperación (RAG) para consultar la información profesional autorizada. RAG es una decisión adoptada por Mario, no una tecnología obligatoria declarada en las instrucciones generales. | F02, F05 | Demostrar que una pregunta activa la recuperación de información antes de generar la respuesta. |
| RAG-02 | El corpus de conocimiento deberá contener únicamente información profesional autorizada y revisada. | F02, F03 | Auditar los documentos incorporados y compararlos con las fuentes aprobadas por Mario. |
| RAG-03 | Cada fragmento del corpus deberá conservar información que permita identificar su documento y sección de origen. | F03 | Inspeccionar los resultados recuperados y comprobar que mantienen trazabilidad hacia su fuente. |
| RAG-04 | El sistema de recuperación deberá localizar fragmentos pertinentes para la pregunta recibida. | F02 | Ejecutar un conjunto de consultas con fragmentos relevantes previamente identificados y comparar los resultados. |
| RAG-05 | La generación de respuestas deberá fundamentarse en la información recuperada y no en datos profesionales no documentados. | F02, F03 | Comparar cada respuesta evaluada con los fragmentos recuperados y detectar afirmaciones sin respaldo. |
| RAG-06 | Cuando la recuperación no encuentre información suficiente, el agente deberá reconocerlo y evitar completar la respuesta con datos inventados. | F02, F03 | Ejecutar preguntas sin respuesta en el corpus y verificar el comportamiento de desconocimiento. |
| RAG-07 | El agente deberá diferenciar las instrucciones del sistema de la información recuperada y no ejecutar instrucciones maliciosas contenidas en documentos o consultas. | F03 | Realizar pruebas de inyección mediante consultas y contenido de recuperación controlado. |
| RAG-08 | La información profesional deberá poder actualizarse sin entrenar nuevamente el modelo de lenguaje. | F02, F03 | Incorporar o modificar una fuente autorizada y comprobar que el cambio pueda reflejarse en la recuperación. |
| RAG-09 | El sistema deberá conservar evidencia suficiente para analizar qué información recuperada sustentó cada respuesta evaluada. | F02, F03 | Revisar el registro de una evaluación y relacionar consulta, fragmentos recuperados y respuesta final. |

## 5. Requisitos de integración

| ID | Requisito | Fuente | Verificación |
|---|---|---|---|
| INT-01 | El agente deberá estar disponible mediante un endpoint HTTP público protegido por HTTPS. | F01 | Acceder al endpoint desde una red externa y verificar una conexión HTTPS válida. |
| INT-02 | El endpoint deberá ser compatible con el contrato Open Responses aceptado por la plataforma de Banorte. | F01 | Registrar el endpoint y completar una conversación desde la plataforma de Banorte. |
| INT-03 | El endpoint deberá validar la estructura y los campos obligatorios de cada solicitud. | F03 | Enviar solicitudes válidas, incompletas y mal formadas y comprobar sus resultados. |
| INT-04 | El endpoint deberá devolver las respuestas con la estructura, encabezados y tipos de contenido requeridos por el contrato de integración. | F01, F04 | Comparar las respuestas con el contrato confirmado y probarlas desde Banorte. |
| INT-05 | El endpoint deberá devolver errores consistentes y códigos HTTP apropiados ante solicitudes inválidas o fallas de procesamiento. | F03 | Provocar cada error previsto y revisar el código y cuerpo recibidos. |
| INT-06 | Cuando se configure autenticación para el agente, el endpoint deberá rechazar solicitudes sin credenciales o con credenciales inválidas. | F01, F04 | Probar solicitudes con credenciales válidas, ausentes e incorrectas. |
| INT-07 | El agente deberá utilizar el historial que reciba conforme al contrato para mantener el contexto de una conversación de varios turnos. | F03, F04 | Ejecutar preguntas dependientes de mensajes anteriores y verificar la continuidad. |
| INT-08 | El endpoint deberá admitir respuestas completas cuando la solicitud no requiera transmisión incremental. | F03, F04 | Enviar una solicitud no incremental y validar la respuesta completa. |
| INT-09 | Si el contrato de Banorte solicita transmisión incremental, el endpoint deberá entregar y finalizar correctamente los eventos esperados. | F04 | Ejecutar una solicitud incremental desde un cliente compatible y validar su secuencia y cierre. |
| INT-10 | El servicio deberá exponer un mecanismo que permita verificar que se encuentra disponible. | F03 | Consultar el mecanismo de salud y comprobar una respuesta exitosa cuando el servicio opere normalmente. |

## 6. Requisitos de calidad y confiabilidad

| ID | Requisito | Fuente | Verificación |
|---|---|---|---|
| CAL-01 | Las respuestas deberán ser claras, naturales, concisas y útiles para conocer la trayectoria profesional de Mario. | F01, F05 | Evaluar las respuestas con una rúbrica definida y ejemplos representativos. |
| CAL-02 | Las respuestas deberán conservar coherencia factual entre preguntas equivalentes y durante una misma conversación. | F01, F03 | Repetir y reformular preguntas y comparar los hechos comunicados. |
| CAL-03 | Las afirmaciones profesionales deberán estar respaldadas por la fuente autorizada o por los fragmentos recuperados. | F01, F02 | Revisar la correspondencia entre afirmaciones, fuentes y recuperación. |
| CAL-04 | El agente deberá responder correctamente en español. | F03 | Ejecutar el banco de evaluación en español y revisar comprensión, redacción y exactitud. |
| CAL-05 | Las respuestas deberán mantenerse enfocadas en la pregunta y evitar contenido innecesario. | F03 | Evaluar relevancia y extensión mediante la rúbrica. |
| CAL-06 | El servicio deberá medir sus tiempos de respuesta para comprobar que resulten adecuados para una conversación interactiva. | F03 | Registrar y reportar la latencia de las pruebas locales y públicas. |
| CAL-07 | El agente deberá permanecer disponible durante el periodo de evaluación y, como compromiso operativo interno, durante al menos 15 días después de la entrega. | F01, F03, F05 | Comprobar periódicamente el acceso al endpoint y registrar su retiro manual al concluir el periodo. |

## 7. Requisitos de seguridad y privacidad

| ID | Requisito | Fuente | Verificación |
|---|---|---|---|
| SEG-01 | Las credenciales y secretos no deberán estar incluidos en el código fuente ni en la base de conocimiento. | F03 | Revisar los archivos del proyecto y ejecutar una búsqueda de secretos antes de la entrega. |
| SEG-02 | El agente deberá separar la información pública autorizada de la información privada o confidencial. | F03 | Auditar el corpus y ejecutar preguntas que intenten obtener información restringida. |
| SEG-03 | Los registros operativos no deberán exponer credenciales ni información sensible. | F03 | Revisar los registros generados durante solicitudes normales y fallidas. |
| SEG-04 | El endpoint deberá limitar o rechazar entradas que excedan los límites establecidos para una solicitud. | F03 | Enviar entradas dentro y fuera del límite y comprobar el comportamiento. |
| SEG-05 | El agente deberá resistir solicitudes que intenten cambiar su propósito, extraer instrucciones internas o forzar la invención de información. | F03 | Ejecutar un conjunto documentado de ataques y verificar que se mantengan las restricciones. |
| SEG-06 | Las respuestas de error no deberán revelar secretos ni detalles internos innecesarios. | F03 | Provocar errores controlados y revisar el contenido devuelto al cliente. |

## 8. Requisitos de evaluación

| ID | Requisito | Fuente | Verificación |
|---|---|---|---|
| EVA-01 | Deberá existir un conjunto reproducible de preguntas y respuestas esperadas para evaluar el agente. | F01, F02, F03 | Revisar el conjunto de evaluación y ejecutar nuevamente las mismas pruebas. |
| EVA-02 | El conjunto de evaluación deberá cubrir perfil, formación, experiencia, habilidades y proyectos. | F01, F02 | Comprobar que exista cobertura de cada categoría en el conjunto de evaluación. |
| EVA-03 | La evaluación deberá incluir preguntas cuya respuesta exista y preguntas cuya respuesta no exista en el corpus. | F02, F03 | Revisar ambos grupos de casos y sus resultados esperados. |
| EVA-04 | La evaluación deberá incluir preguntas de seguimiento, fuera de dominio, ambiguas, confidenciales y adversariales. | F03 | Comprobar que cada categoría tenga casos y resultados documentados. |
| EVA-05 | La calidad del proceso de recuperación deberá evaluarse por separado de la calidad de la respuesta generada. | F02 | Reportar resultados diferenciados para recuperación y generación. |
| EVA-06 | La evaluación de recuperación deberá medir si los fragmentos relevantes aparecen entre los resultados obtenidos para cada consulta. | F02 | Comparar los fragmentos recuperados con la relevancia esperada definida en el conjunto de evaluación. |
| EVA-07 | La evaluación de generación deberá medir exactitud, fundamentación, relevancia, claridad y manejo de información desconocida. | F01, F02, F03 | Aplicar una rúbrica consistente a las respuestas obtenidas. |
| EVA-08 | La evaluación de extremo a extremo deberá comprobar que una pregunta produce una recuperación pertinente y una respuesta respaldada. | F02 | Relacionar consulta, recuperación y respuesta en cada caso evaluado. |
| EVA-09 | La evaluación deberá registrar latencia, errores y casos sin respuesta. | F03 | Generar un reporte con tiempos, fallas y resultado por caso. |
| EVA-10 | Los criterios y umbrales de aceptación deberán quedar definidos antes de ejecutar la evaluación final. | F02, F03 | Revisar que la rúbrica y los umbrales tengan una versión y fecha anteriores al reporte final. |
| EVA-11 | La evaluación completa deberá poder repetirse después de cualquier cambio relevante para detectar regresiones. | F02, F03 | Ejecutar el mismo conjunto antes y después de un cambio y comparar los resultados. |
| EVA-12 | La ponderación interna deberá distinguirse explícitamente de cualquier rúbrica oficial de Banorte. | F05 | Revisar `docs/criterios-evaluacion.md`, el README y la presentación para evitar atribuir a Banorte porcentajes no publicados. |

## 9. Requisitos pendientes de confirmación con Banorte

Los siguientes elementos forman parte del contrato de integración, pero sus valores exactos no deben asumirse hasta observar solicitudes y respuestas aceptadas por la plataforma:

- Versión o subconjunto de Open Responses utilizado por Banorte.
- Esquema exacto de solicitud y respuesta, incluidos campos opcionales.
- Serialización exacta de la transcripción dentro de `input`.
- Encabezados reales recibidos, aunque el formulario ya confirma el uso posible de Bearer.
- Uso real de transmisión incremental y secuencia de eventos SSE consumida.
- Límites de tamaño, frecuencia, duración y tiempo de respuesta.
- Formato de errores mostrado o interpretado por la plataforma.
- Inclusión de capacidades fuera del MVP, como herramientas, WebSockets o compactación.

## 10. Compromisos de entrega y operación

Estos compromisos fueron adoptados por Mario y no deberán presentarse como una rúbrica oficial no publicada:

| ID | Compromiso | Fuente | Verificación |
|---|---|---|---|
| ENT-01 | El repositorio entregado será público y deberá estar sanitizado antes de publicarse. | F05 | Auditar archivos, historial y secretos antes de habilitar el acceso público. |
| ENT-02 | El repositorio incluirá un README reproducible, decisiones técnicas, arquitectura y evidencia de evaluación. | F05 | Ejecutar las instrucciones desde una instalación limpia y revisar enlaces y evidencias. |
| ENT-03 | La presentación explicará resultados, arquitectura, alternativas y trade-offs. | F05 | Comparar la presentación con `docs/criterios-evaluacion.md`. |
| ENT-04 | El video o demostración en vivo se preparará después de estabilizar la implementación y la integración. | F05 | Comprobar que no bloquee las tareas técnicas críticas actuales. |
| ENT-05 | El endpoint permanecerá disponible durante al menos 15 días después de la entrega y será retirado manualmente por Mario. | F05 | Registrar comprobaciones de disponibilidad y la fecha de retiro. |
