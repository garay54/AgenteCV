# Alcance del MVP — Agente de CV Banorte

## 1. Definición del MVP

El MVP será un agente de CV accesible mediante una API pública HTTPS compatible con Open Responses que, utilizando RAG sobre información profesional verificada de Mario, responda en español preguntas de texto claras y concisas sobre su perfil, formación, experiencia, habilidades y proyectos, mantenga el contexto recibido y reconozca explícitamente cuando no disponga de información.

## 2. Capacidades incluidas

- Endpoint público mediante HTTPS.
- Compatibilidad con el contrato Open Responses requerido por Banorte.
- Conversación de texto en español.
- Identificación explícita como agente profesional de Mario y uso consistente de primera persona al describir su trayectoria.
- Respuestas sobre el perfil profesional de Mario.
- Respuestas sobre su formación académica documentada.
- Respuestas sobre su experiencia laboral.
- Respuestas sobre sus habilidades técnicas y profesionales.
- Respuestas sobre sus proyectos y resultados verificables.
- Recuperación RAG sobre fuentes profesionales autorizadas.
- Respuestas fundamentadas en la información recuperada.
- Reconocimiento explícito de información desconocida.
- Prevención de afirmaciones profesionales no respaldadas.
- Resistencia a solicitudes para revelar información confidencial, inventar experiencia o cambiar el propósito del agente.
- Manejo de preguntas fuera del alcance profesional.
- Uso de la transcripción recibida para mantener el contexto de varios turnos.
- Autenticación mediante Bearer token al integrarse con Banorte.
- Respuesta no streaming compatible con el contrato.
- Streaming SSE cuando sea solicitado por la plataforma y confirmado mediante pruebas.
- Manejo consistente de solicitudes inválidas y errores.
- Evaluación de recuperación RAG y calidad de las respuestas.
- Registro de evidencia suficiente para demostrar el cumplimiento del MVP.

## 3. Fuera del alcance inicial

- Interfaz gráfica propia.
- Aplicación móvil.
- Entrada de imágenes.
- Entrada o entrega de archivos.
- Memoria conversacional persistente.
- Uso de `previous_response_id` en el MVP.
- Registro o inicio de sesión de usuarios finales.
- Panel administrativo.
- Herramientas externas distintas de la recuperación de conocimiento requerida.
- Acciones con efectos externos.
- WebSockets.
- Endpoint de compactación de conversaciones.
- Soporte de voz, audio o video.
- Integraciones adicionales fuera de la plataforma de Banorte.

Un elemento fuera del alcance sólo podrá incorporarse si resulta obligatorio para la integración, corrige un riesgo crítico o sustituye una capacidad incluida sin ampliar el tiempo de entrega.

## 4. Criterios de aceptación del MVP

El MVP se considerará funcional cuando:

- Banorte pueda enviar una pregunta al endpoint y mostrar su respuesta.
- El endpoint público responda mediante HTTPS y cumpla el contrato aplicable.
- La autenticación configurada acepte la clave correcta y rechace claves ausentes o incorrectas.
- El agente responda correctamente preguntas representativas sobre perfil, formación, experiencia, habilidades y proyectos.
- Las respuestas sean claras, coherentes, concisas y directamente relacionadas con la pregunta.
- La recuperación RAG encuentre información pertinente en casos conocidos.
- Las respuestas estén respaldadas por la información recuperada.
- El agente reconozca datos ausentes en lugar de inventarlos.
- El agente no divulgue información confidencial ni afirme ser una persona humana.
- Una conversación de varios turnos conserve contexto mediante la transcripción recibida.
- La respuesta no streaming sea aceptada por Banorte.
- El streaming funcione si Banorte lo solicita durante la integración.
- Los errores principales produzcan respuestas controladas y comprensibles.
- Las evaluaciones críticas alcancen los criterios definidos antes de la evaluación final.

## 5. Restricciones de alcance

- El agente sólo utilizará información profesional autorizada por Mario.
- No se incluirá información confidencial, privada o no verificable.
- No se ampliará el alcance para incorporar tecnologías únicamente con fines demostrativos.
- Las capacidades pendientes de confirmación se mantendrán como supuestos hasta obtener evidencia.
- Las decisiones técnicas se documentarán por separado y no modificarán esta definición sin registrar el cambio.

## 6. Compromisos de entrega y operación

- El repositorio final será público, pero sólo después de auditar secretos, fuentes privadas e historial de Git.
- El repositorio incluirá README, decisiones, arquitectura y evidencia reproducible de evaluación.
- La presentación explicará funcionamiento, resultados, alternativas y trade-offs.
- El video o demostración en vivo se preparará después de estabilizar la integración.
- El endpoint permanecerá disponible durante al menos 15 días después de la entrega y Mario lo retirará manualmente al concluir ese periodo.

## 7. Documentos relacionados

- `docs/requisitos.md`
- `docs/contrato-open-responses.md`
- `docs/dudas-y-supuestos.md`
- `docs/criterios-evaluacion.md`

## 8. Historial de cambios

| Fecha | Cambio | Responsable |
|---|---|---|
| 2026-08-17 | Definición inicial del alcance del MVP. | Mario |
| 2026-08-18 | Se incorporaron identidad, claridad, seguridad, entregables y disponibilidad mínima de 15 días. | Mario |
