# Dudas y supuestos — Agente de CV

## 1. Propósito

Este documento registra las preguntas que todavía no tienen una respuesta confirmada y los supuestos temporales utilizados para poder avanzar. Su finalidad es evitar que una interpretación provisional se trate como un requisito confirmado o como una decisión definitiva.

## 2. Estados

- **Abierta:** todavía no existe una respuesta confirmada.
- **En validación:** se está obteniendo o comprobando evidencia.
- **Confirmada:** existe evidencia que respalda el supuesto.
- **Rechazada:** la evidencia demostró que el supuesto era incorrecto.
- **Cerrada:** la duda fue respondida y los documentos relacionados fueron actualizados.

## 3. Preguntas abiertas

| ID | Pregunta | Por qué importa | Cómo obtener la respuesta | Estado |
|---|---|---|---|---|
| DUD-001 | ¿Qué versión de Open Responses evaluará la plataforma cliente? | La versión actual incluye capacidades que podrían no formar parte del reto. | Revisar documentación de la plataforma cliente o ejecutar su integración real. | Abierta |
| DUD-002 | ¿La plataforma cliente solicitará `stream: true`? | Determina si el agente debe producir eventos SSE durante la evaluación. | Una solicitud real utilizó streaming y la interfaz aceptó la secuencia SSE desplegada. | Cerrada |
| DUD-003 | ¿Cuál es el cuerpo JSON exacto enviado por la plataforma cliente? | Define los campos que debe aceptar el endpoint. | Registrar de forma sanitizada una solicitud real. | Abierta |
| DUD-004 | ¿Cuál es el tiempo máximo de respuesta? | Una respuesta lenta podría ser cancelada por la plataforma. | Medir pruebas reales y solicitar confirmación a la plataforma cliente. | Abierta |
| DUD-005 | ¿Qué límites existen para tamaño y frecuencia de solicitudes? | Afecta la validación, los costos y el manejo de errores. | Revisar documentación y realizar pruebas controladas. | Abierta |
| DUD-006 | ¿La plataforma cliente evaluará herramientas, imágenes, WebSockets o compactación? | Podría ampliar significativamente el alcance del MVP. | Consultar a la plataforma cliente o identificar las pruebas ejecutadas por la plataforma. | Abierta |
| DUD-007 | ¿Cuál es la respuesta mínima aceptada y cómo interpreta la plataforma cliente los errores? | Define los campos de salida y el comportamiento ante fallas. | Conectar un MVP sonda, probar respuestas controladas y guardar evidencia sanitizada. | Abierta |

## 4. Supuestos de trabajo

| ID | Supuesto | Motivo | Riesgo si es incorrecto | Cómo se validará | Estado |
|---|---|---|---|---|---|
| SUP-001 | Se utilizará como referencia Open Responses `2026-04-24`. | Es la versión publicada actualmente. | La plataforma cliente podría utilizar una versión o un subconjunto diferente. | Ejecutar las pruebas de aceptación aplicables y probar el endpoint desde la plataforma cliente. | Abierta |
| SUP-002 | La plataforma cliente agregará `/responses` a una URL base terminada en `/v1`. | El formulario muestra que las solicitudes se envían a `{base URL}/responses`. | Una URL mal formada produciría un error 404 o una ruta duplicada. | La ruta pública fue invocada correctamente desde el cliente conversacional. | Confirmada |
| SUP-003 | La plataforma cliente reenviará la transcripción completa en cada turno. | Se seleccionó “Reproducir transcripción (sin estado)”. | El agente podría perder el contexto si la transcripción fuera incompleta. | Ejecutar una conversación de varios turnos e inspeccionar la segunda solicitud. | Abierta |
| SUP-004 | El agente sólo necesitará aceptar texto en el MVP. | El reto solicita conversación sobre la trayectoria y las entradas de archivos e imágenes permanecerán desactivadas. | La evaluación podría enviar otra modalidad no soportada. | Probar la integración y confirmar el alcance con la plataforma cliente. | Abierta |
| SUP-005 | La API key será enviada mediante `Authorization: Bearer`. | El formulario de la plataforma cliente lo declara explícitamente. | Una diferencia de formato impediría autenticar solicitudes válidas. | Observar el encabezado recibido y probar una solicitud autenticada. | Confirmada |
| SUP-006 | El campo `model` podrá omitirse. | El formulario lo presenta como opcional. | El endpoint podría rechazar solicitudes sin modelo o la plataforma cliente podría enviar un valor inesperado. | Probar solicitudes con y sin `model`. | Abierta |
| SUP-007 | RAG y su evaluación forman parte del alcance técnico elegido. | Fue indicado durante el proceso de entrevista y Mario confirmó que desea utilizarlo aunque no sea una tecnología obligatoria general. | La implementación podría dedicar tiempo a una capacidad que la plataforma cliente evalúe de forma distinta. | Demostrar recuperación y fundamentación mediante la rúbrica interna. | Confirmada |

## 5. Elementos confirmados que ya no son dudas

| ID relacionado | Resultado confirmado | Fuente |
|---|---|---|
| R07 | La plataforma permite reproducir la transcripción o utilizar `previous_response_id`. | Formulario “Añadir un agente” de la plataforma cliente. |
| R08 | La plataforma puede enviar una API key mediante `Authorization: Bearer <API_KEY>`. | Formulario “Añadir un agente” de la plataforma cliente. |
| R08 | El campo de API key es opcional en el formulario y la plataforma cliente indica que la almacena cifrada. | Formulario “Añadir un agente” de la plataforma cliente. |
| R09 | La plataforma cliente proporciona el chat desde el que se selecciona y prueba el agente; no se requiere frontend propio para el MVP. | Instrucciones oficiales del reto y formulario de la plataforma cliente. |
| R10 | No existe una regla confirmada sobre primera o tercera persona. Mario eligió primera persona por defecto con identificación explícita como agente profesional. | Respuesta del agente Guía y decisión directa de Mario. |
| R11 | No existe una rúbrica oficial detallada ni ponderaciones publicadas en la información disponible. | Respuesta del agente Guía; la ponderación del proyecto es interna. |

## 6. Decisiones de Mario que no son requisitos oficiales

| ID | Decisión | Estado |
|---|---|---|
| DEC-M01 | Utilizar RAG ligero y evaluarlo de forma reproducible. | Aceptada |
| DEC-M02 | No construir frontend propio; utilizar el chat de la plataforma cliente. | Aceptada |
| DEC-M03 | Responder en primera persona por defecto, identificándose como agente y sin afirmar que es una persona humana. | Aceptada |
| DEC-M04 | Utilizar una rúbrica interna con énfasis en calidad, arquitectura, despliegue, seguridad y documentación. | Aceptada |
| DEC-M05 | Publicar un repositorio sanitizado con README y preparar una presentación con evaluación. | Aceptada |
| DEC-M06 | Mantener el endpoint disponible durante al menos 15 días después de la entrega y retirarlo manualmente. | Aceptada |

## 7. Regla de actualización

Cuando una duda o un supuesto sea validado:

1. Cambiar su estado.
2. Registrar la evidencia obtenida en el historial.
3. Actualizar `docs/requisitos.md` o `docs/contrato-open-responses.md`.
4. Registrar una decisión en `docs/decisiones.md` si la evidencia obliga a elegir una alternativa.
5. No eliminar el registro original; conservarlo como historial del proyecto.

## 8. Historial

| Fecha | ID | Resultado | Evidencia |
|---|---|---|---|
| 2026-08-17 | R07 | Se identificaron las modalidades “Reproducir transcripción (sin estado)” y `previous_response_id`. | Captura del formulario de la plataforma cliente. |
| 2026-08-17 | R08 | Se confirmó el formato `Authorization: Bearer <API_KEY>`. | Captura del formulario de la plataforma cliente. |
| 2026-08-18 | R09–R11 | Se separaron las capacidades confirmadas de la plataforma, la orientación general del agente Guía y las decisiones propias de Mario. | Instrucciones del reto, formulario, conversación con el agente Guía y confirmación directa de Mario. |
| 2026-08-20 | R06, DUD-002, SUP-002 | Se confirmaron la ruta pública, la integración autenticada y el streaming SSE. | Conversación funcional desde el cliente conversacional. |
