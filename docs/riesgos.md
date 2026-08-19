# Registro de riesgos — Agente de CV Banorte

## 1. Propósito

Este documento identifica los riesgos que pueden impedir que el agente funcione, se integre con Banorte o sea demostrado antes del miércoles 19 de agosto de 2026 a las 12:00, hora de Chihuahua.

La mitigación reduce la probabilidad o el impacto antes de que ocurra el problema. La contingencia describe qué hacer cuando el problema ya ocurrió.

## 2. Escala de prioridad

- **Crítica:** puede impedir la entrega, exponer información o invalidar la solución.
- **Alta:** afecta una capacidad principal o la demostración, pero permite recuperación.
- **Media:** degrada calidad, costo o experiencia sin impedir necesariamente la entrega.

## 3. Riesgos prioritarios

| ID | Riesgo | Prioridad | Señal de detección | Mitigación | Contingencia | Evidencia requerida | Estado |
|---|---|---|---|---|---|---|---|
| RK-01 | Cuota o límite del modelo agotado | Alta | Respuesta `429`, rechazo por límite o ausencia de créditos | Vigilar el consumo, limitar el tamaño de las respuestas y evitar llamadas reales durante pruebas deterministas | Devolver un error controlado; ejecutar las pruebas con el proveedor simulado y conservar evidencia previa para la demo | Prueba del error `429`, configuración de límites y resultado de una prueba simulada | Pendiente de verificar |
| RK-02 | Clave o secreto expuesto | Crítica | Una credencial aparece en Git, código, capturas, respuestas o logs | Mantener secretos en variables de entorno, excluir `.env` de Git y usar el gestor de secretos del despliegue | Revocar y reemplazar la credencial; eliminarla de las superficies públicas y revisar dónde fue utilizada | `.gitignore`, `.env.example`, revisión del repositorio y captura segura de la configuración | Pendiente de verificar |
| RK-03 | Cold start demasiado lento | Alta | La primera solicitud después de inactividad supera el tiempo aceptado por la plataforma | Medir solicitudes después de inactividad y seleccionar una configuración de despliegue compatible con el tiempo disponible | Calentar el servicio antes de la demo; mostrar evidencia previa si la plataforma tarda en iniciar | Registro de primera respuesta, tiempo total y comparación con una solicitud posterior | Pendiente de medir |
| RK-04 | Timeout del modelo o del endpoint | Alta | Solicitud sin respuesta dentro del tiempo máximo o error de conexión | Configurar tiempos máximos explícitos y reintentos limitados únicamente para fallos temporales | Cancelar la espera y devolver un error seguro, identificable y recuperable | Prueba de timeout, código HTTP esperado y log asociado mediante ID de solicitud | Pendiente de verificar |
| RK-05 | Alucinación sobre trayectoria, fechas o tecnologías | Crítica | La respuesta afirma un dato que no aparece en las fuentes profesionales | Usar RAG sobre fuentes revisadas, aplicar una política de incertidumbre y evaluar preguntas conocidas, desconocidas y engañosas | Reconocer que no existe información suficiente, retirar la afirmación y corregir recuperación o instrucciones antes de desplegar | Casos de evaluación, fragmentos recuperados y comparación de respuesta contra la fuente | Pendiente de evaluar |
| RK-06 | Exposición de datos confidenciales | Crítica | El agente, los documentos o los logs muestran datos personales, credenciales o información no publicable | Limpiar las fuentes antes de indexarlas, excluir datos sensibles, proteger logs y probar intentos de extracción | Retirar el dato, reemplazar el índice o documento afectado y rotar credenciales cuando corresponda | Revisión de fuentes, pruebas de extracción y muestra de logs sin contenido sensible | Pendiente de verificar |
| RK-07 | Caída o indisponibilidad del proveedor de IA | Alta | Error de conexión, timeout, respuesta `5xx` o estado inválido del proveedor | Distinguir errores del proveedor, aplicar timeouts y reintentos limitados, y mantener pruebas independientes de la red | Devolver un error controlado; utilizar respuestas y evidencia previamente guardadas para explicar la solución durante la demo | Prueba simulada de indisponibilidad, respuesta segura y log asociado | Pendiente de verificar |
| RK-08 | Incompatibilidad con el contrato Open Responses de Banorte | Crítica | La plataforma rechaza el endpoint, no interpreta la respuesta o corta el streaming | Implementar el contrato documentado y aislar la transformación de entrada y salida del núcleo del agente | Observar solicitudes reales, corregir sólo el adaptador del contrato y repetir la prueba en Banorte | Solicitud y respuesta aceptadas, logs seguros y captura de una conversación funcional | Pendiente de integrar |
| RK-09 | Recuperación RAG irrelevante o incompleta | Crítica | La respuesta usa fragmentos incorrectos o no encuentra información que sí existe | Evaluar recuperación por separado, conservar metadatos de origen y ajustar la preparación o búsqueda con casos reales | Responder con incertidumbre cuando la evidencia recuperada sea insuficiente y corregir el caso antes de la regresión final | Conjunto de consultas, resultados esperados, fragmentos recuperados y métricas definidas | Pendiente de evaluar |
| RK-10 | Endpoint público abusado o utilizado sin autorización | Alta | Solicitudes con credenciales inválidas, volumen anormal o aumento inesperado de consumo | Validar el mecanismo de autenticación aceptado por Banorte, no registrar secretos y limitar el consumo cuando sea posible | Reemplazar la clave de entrada, bloquear solicitudes inválidas y revisar logs y costos | Pruebas `401`, configuración segura y logs sin credenciales | Pendiente de verificar |
| RK-11 | Fallo de despliegue o URL pública inestable | Alta | `/health` no responde, cambia la URL, faltan variables o el servicio no inicia | Probar el contenedor localmente, documentar variables y revisar puerto, comando y logs del despliegue | Corregir únicamente configuración crítica y volver a la última versión pública funcional | Prueba externa de `/health`, URL registrada y logs del despliegue | Pendiente de desplegar |
| RK-12 | Retraso del cronograma | Crítica | Una etapa termina después de su hora y bloquea las siguientes | Priorizar las actividades críticas, exigir un resultado demostrable por etapa y retirar extras del MVP | Mover mejoras no críticas fuera del alcance; congelar funciones el miércoles a las 11:15 | Avance del checklist, resultados por etapa y versión pública del martes | En seguimiento |

## 4. Orden de atención

Antes de desplegar deben estar mitigados y comprobados, como mínimo:

1. `RK-02` — exposición de claves o secretos.
2. `RK-05` — alucinaciones.
3. `RK-06` — datos confidenciales.
4. `RK-08` — contrato incompatible.
5. `RK-09` — recuperación RAG incorrecta.
6. `RK-12` — retraso que impida llegar a una versión pública.

Antes de la demostración deben revisarse también `RK-01`, `RK-03`, `RK-04`, `RK-07`, `RK-10` y `RK-11`.

## 5. Regla de actualización

Cada vez que un riesgo se pruebe:

1. Cambiar su estado a **Mitigado** sólo si existe evidencia.
2. Anotar la ubicación de la prueba, captura, log o configuración.
3. Registrar cualquier riesgo nuevo descubierto durante pruebas o integración.
4. Reabrir el riesgo si cambia el contrato, el modelo, el RAG o el despliegue.

## 6. Criterio de terminado para P07

La actividad `P07` se considera terminada cuando:

- Los riesgos prioritarios están registrados.
- Cada riesgo tiene una mitigación y una contingencia.
- Cada mitigación tiene una evidencia esperada.
- Los estados distinguen claramente lo pendiente de lo comprobado.

