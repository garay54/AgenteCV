# Cronograma de entrega — Agente de CV Banorte

## 1. Fecha límite

- **Límite interno:** miércoles 19 de agosto de 2026 a las 12:00, hora de Chihuahua.
- **Inicio del plan acelerado:** lunes 17 de agosto de 2026 a las 23:30.
- **Punto de congelamiento:** miércoles 19 de agosto de 2026 a las 11:15.

El objetivo es terminar el martes con una versión pública demostrable y utilizar la mañana del miércoles exclusivamente para integrar, corregir, evaluar y congelar la entrega.

## 2. Regla de ejecución

- Cada bloque debe cerrar con el resultado indicado antes de comenzar el siguiente.
- Si una actividad no crítica se retrasa, se mueve a la lista de mejoras y no bloquea el MVP.
- R06 permanece en progreso hasta probar solicitudes y respuestas reales con Banorte.
- Después de las 11:15 del miércoles no se agregan funciones; sólo se aceptan correcciones críticas.

## 3. Agenda por etapas

| Etapa | Fecha y hora | Objetivo | Actividades que deben concluir | Resultado demostrable |
|---|---|---|---|---|
| 0. Cerrar alcance | Lun 17, 23:30 → Mar 18, 00:30 | Congelar requisitos, alcance y plan | `R03–R05`, `R07–R10`, `P01–P08`, `C01–C02` | Requisitos, contrato, supuestos, alcance, cronograma y fuentes reunidas. |
| 1. Fuente profesional | Mar 18, 08:00–10:00 | Preparar la fuente de verdad | `C03–C11` | Conocimiento revisado y banco inicial de preguntas. |
| 2. Arquitectura y API base | Mar 18, 10:00–13:00 | Obtener el primer contrato ejecutable | `D01–D10`, `S01–S02`, `S04–S11`, `A01–A10`, `I12` | `/health` y `/v1/responses` funcionan localmente con proveedor simulado. |
| 3. RAG y modelo | Mar 18, 14:00–17:00 | Responder preguntas reales del CV | `I01–I05`, `I07–I09`, `I11`, `B01–B10` | El agente recupera contexto, responde y reconoce información desconocida. |
| 4. Seguridad y pruebas base | Mar 18, 17:00–19:00 | Proteger y estabilizar el servicio | `I06`, `I10`, `G01–G07`, `G09–G10`, `E01–E03`, `E05–E06` | Autenticación, errores y pruebas fundamentales funcionan localmente. |
| 5. Contrato y streaming | Mar 18, 19:00–21:00 | Completar Open Responses | `A11`, `T01`, `T03–T06`, `T08`, `E04`, `E11` | Respuesta completa, historial y SSE pasan pruebas locales. |
| 6. Despliegue público | Mar 18, 21:00–23:00 | Publicar la versión demostrable | `S03`, `S12`, `H01–H04`, `H06–H09`, `H12` | URL HTTPS pública, secretos configurados y repositorio actualizado. |
| 7. Integración Banorte | Mié 19, 07:00–08:30 | Conectar el agente real | `N01–N03`, `N05–N07` | Banorte muestra respuestas del agente y existe evidencia. |
| 8. Corrección de contrato | Mié 19, 08:30–09:30 | Resolver diferencias observadas | `R06`, `N04`, `H10–H11` | Ejemplos aceptados, streaming confirmado y contrato cerrado. |
| 9. Evaluación final | Mié 19, 09:30–10:30 | Comprobar calidad y regresiones | `E07–E10`, `E13–E14` | Banco crítico ejecutado con resultados guardados. |
| 10. Documentación y demo | Mié 19, 10:30–11:15 | Preparar la defensa de la solución | `M01–M10`, `F01–F08` | README completo, explicación preparada y demo ensayada. |
| 11. Congelamiento | Mié 19, 11:15–12:00 | Proteger la versión final | `F09–F12` | Clon limpio probado, humo final ejecutado y versión congelada. |

## 4. Actividades que no deben bloquear el MVP

Estas actividades sólo se realizan si las exige la integración o existe tiempo de contingencia:

- `T02` — Estrategia avanzada para conversaciones largas.
- `T07` — Manejo completo de cancelación y desconexión.
- `G08` — Rate limiting avanzado.
- `E12` — Evaluación bilingüe.
- `H05` — Optimización adicional del usuario y tamaño del contenedor.
- Capacidades de imágenes, archivos, WebSockets y compactación.

## 5. Hitos obligatorios

### Martes 18 a las 13:00

- API local ejecutable.
- `/health` disponible.
- `/v1/responses` validado con respuesta simulada.

### Martes 18 a las 17:00

- RAG funcional.
- Primera respuesta real del modelo.
- Manejo de información desconocida.

### Martes 18 a las 23:00

- URL HTTPS pública.
- Autenticación configurada.
- Pruebas de humo públicas.
- Repositorio actualizado.

### Miércoles 19 a las 09:30

- Agente registrado en Banorte.
- Contrato corregido con evidencia real.
- R06 cerrado.

### Miércoles 19 a las 11:15

- Regresión final aprobada.
- README y evidencias terminados.
- Demo ensayada.

### Miércoles 19 a las 12:00

- Versión congelada y reproducible.
- Contingencia preparada.
- Entrega lista para confirmarse.

## 6. Contingencia

- Si RAG no está listo el martes a las 17:00, reducir el corpus a las fuentes profesionales esenciales y conservar la evaluación mínima.
- Si streaming falla a las 21:00, preservar la respuesta no streaming y continuar sólo si Banorte confirma que streaming es obligatorio.
- Si el despliegue principal falla, utilizar una segunda opción de alojamiento sin cambiar la aplicación.
- Si Banorte no responde, demostrar el endpoint público con solicitudes guardadas y conservar logs sanitizados.
- Si una mejora no corrige un riesgo crítico antes del congelamiento, se documenta como trabajo futuro.

## 7. Historial de cambios

| Fecha | Cambio | Responsable |
|---|---|---|
| 2026-08-17 | Cronograma acelerado definido hasta el miércoles a las 12:00. | Mario |
