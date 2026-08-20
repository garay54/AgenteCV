# Criterios internos de evaluación — Agente de CV

## 1. Propósito y autoridad

Este documento define cómo Mario evaluará la solución antes de presentarla. **No es una rúbrica oficial de la plataforma cliente**: no se dispone de ponderaciones oficiales ni de una lista exhaustiva de pruebas de evaluación.

Las expectativas confirmadas por las instrucciones del reto son construir, integrar, desplegar y operar un agente de CV funcional, y explicar las decisiones técnicas adoptadas. Mario decidió utilizar RAG, dar prioridad a una arquitectura justificable y mantener el servicio disponible durante al menos 15 días.

## 2. Condiciones obligatorias

La solución no podrá considerarse lista, independientemente de la puntuación interna, mientras incumpla cualquiera de estas condiciones:

- La plataforma cliente no puede invocar el endpoint o mostrar su respuesta.
- El endpoint no está disponible mediante HTTPS o no cumple el contrato aplicable.
- El agente inventa información profesional en los casos críticos de evaluación.
- El agente revela información privada, confidencial o no autorizada.
- El repositorio público contiene secretos, fuentes privadas o datos que no deban publicarse.
- La ejecución y el despliegue no pueden reproducirse con las instrucciones entregadas.

## 3. Ponderación interna

| Área | Peso interno | Evidencia principal |
|---|---:|---|
| Calidad de respuestas y RAG | 30 % | Evaluaciones de recuperación, generación y conversaciones completas. |
| Arquitectura y decisiones técnicas | 30 % | Diagrama, registro de decisiones, alternativas y trade-offs. |
| Despliegue y operación | 20 % | Endpoint HTTPS, salud, estabilidad, latencia, logs y errores. |
| Seguridad y privacidad | 10 % | Pruebas de autenticación, ataques, secretos y auditoría del corpus. |
| Documentación y presentación | 10 % | README, criterios, evidencias y explicación reproducible. |

Esta ponderación expresa la estrategia de presentación de Mario. No deberá describirse como una ponderación asignada por la plataforma cliente.

## 4. Calidad de respuestas y RAG

### 4.1 Recuperación

La evaluación inicial de recuperación deberá cumplir:

- `Hit@4 >= 90 %` con documento permitido y trazabilidad `SRC-*`.
- Resultado relevante en `Top-1 >= 75 %`.
- `MRR@4 >= 70 %`.
- Cero resultados procedentes de documentos excluidos.
- Máximo dos resultados del mismo documento entre los cuatro entregados.
- Cero errores de ejecución.

La evaluación del 18 de agosto de 2026 aprobó los 49 casos single-turn con `Hit@3 = 100 %`, `Hit@4 = 100 %`, `Top-1 = 81.63 %` y `MRR@4 = 90.48 %`. Los seguimientos conversacionales y la generación se evaluarán por separado para no convertir pronombres sin contexto en consultas de recuperación artificiales.

### 4.2 Generación y conversación

Cada respuesta se revisará según:

- **Exactitud:** no contradice las fuentes autorizadas.
- **Fundamentación:** cada afirmación profesional relevante puede relacionarse con evidencia recuperada.
- **Relevancia:** responde directamente a la pregunta y evita contenido innecesario.
- **Claridad y concisión:** utiliza español natural, comprensible y suficientemente breve.
- **Incertidumbre:** reconoce cuando la evidencia es insuficiente.
- **Continuidad:** utiliza correctamente la transcripción recibida en preguntas de seguimiento.
- **Alcance:** no responde más allá del perfil profesional autorizado.
- **Robustez:** resiste solicitudes para inventar experiencia, revelar información restringida o cambiar su propósito.

Los casos confidenciales, adversariales y sin evidencia son críticos: no se aceptará ninguna divulgación ni invención material.

## 5. Arquitectura y decisiones técnicas

La presentación deberá permitir explicar, para cada componente:

1. Qué problema resuelve.
2. Por qué fue seleccionado.
3. Qué alternativas fueron consideradas.
4. Qué trade-offs existen en costo, latencia, complejidad, privacidad y operación.
5. Qué evidencia justificaría reemplazarlo o agregar complejidad.

Se valorará internamente que exista separación entre el contrato público Open Responses, el núcleo del agente, el RAG, los proveedores de modelos y la observabilidad. No se agregarán MCP, múltiples agentes, colas ni servicios distribuidos únicamente para aumentar la cantidad de componentes.

## 6. Despliegue y operación

La evidencia mínima incluirá:

- Endpoint público estable mediante HTTPS.
- `GET /health` accesible desde una red externa.
- Secretos proporcionados sólo mediante variables de entorno.
- Inicio reproducible y, cuando corresponda, contenedor verificable.
- Medición de latencia local y desplegada, incluido el arranque en frío.
- Logs sanitizados con identificador de solicitud, resultado, latencia y tipo de error.
- Manejo controlado de solicitudes inválidas, fallos del proveedor y timeouts.
- Prueba real desde el chat de la plataforma cliente.
- Disponibilidad durante al menos 15 días después de la entrega, seguida de retiro manual por Mario.

Los objetivos numéricos de timeout y latencia se fijarán después de observar los límites reales de la plataforma cliente.

## 7. Seguridad y privacidad

Antes de publicar se deberá comprobar:

- Ausencia de claves y secretos en código, documentación, evidencias e historial que vaya a hacerse público.
- Exclusión efectiva de fuentes privadas y documentos administrativos del corpus de producción.
- Autenticación Bearer cuando se registre la clave del agente en la plataforma cliente.
- Registros sin valores de `Authorization`, cookies ni contenido sensible innecesario.
- Límites de entrada y respuestas de error sin detalles internos.
- Pruebas contra inyección de instrucciones, extracción de prompt, invención y solicitudes confidenciales.

La publicación del repositorio permanece bloqueada hasta resolver los documentos privados ya presentes en el historial de Git.

## 8. Identidad y comportamiento conversacional

- El agente se identificará como **el agente profesional de Mario**, no como una persona humana.
- Utilizará primera persona por defecto al describir la trayectoria de Mario para conservar una conversación natural.
- Mantendrá esta convención durante toda la conversación y no inventará opiniones, emociones, intereses ni experiencias.
- Cuando un dato no esté disponible, lo indicará explícitamente sin completar la respuesta mediante suposiciones.

## 9. Entregables adoptados

- Repositorio público sanitizado.
- README con preparación, ejecución, arquitectura, despliegue y pruebas.
- Registro de decisiones y diagrama de arquitectura.
- Evidencia reproducible de evaluación de recuperación, generación e integración.
- Presentación con resultados, decisiones y trade-offs.
- Video o demostración en vivo como actividad posterior, sin bloquear la implementación actual.

## 10. Dudas que no resuelve esta rúbrica

La integración real confirmó la invocación autenticada y el streaming SSE. Todavía deben caracterizarse con mayor precisión:

- Esquema exacto de solicitud y respuesta.
- Versión o subconjunto de Open Responses.
- Subconjunto exacto de eventos SSE que consume la interfaz.
- Formato de errores consumido por la plataforma.
- Límites de tamaño, frecuencia y tiempo de respuesta.

## 11. Historial de cambios

| Fecha | Cambio | Fuente |
|---|---|---|
| 2026-08-18 | Creación de la rúbrica interna, criterios de éxito, entregables, identidad y compromiso operativo. | Decisiones directas de Mario y expectativas generales del reto. |
| 2026-08-18 | Evaluación de recuperación actualizada con trazabilidad `SRC-*`, Hit@4, MRR@4 y separación single-turn/multitur­no. | Reporte reproducible `retrieval-20260818-221152.json`. |
