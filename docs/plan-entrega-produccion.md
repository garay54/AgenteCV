# Plan de entrega inmediata a producción controlada

## 1. Objetivo

Entregar una versión sanitizada del proyecto de agente conversacional sin cambiar las rutas públicas, la autenticación, los modelos HTTP ni los eventos SSE ya aceptados por el cliente conversacional.

El despliegue funcional de referencia corresponde al commit `9c5d333c814323a4440ed720e689169ad8c89a17`. Esta referencia permite regresar a la versión anterior si la reconstrucción del índice o la integración presentan una regresión.

## 2. Congelamiento de versión

- [x] Registrar el commit y el endpoint del despliegue funcional anterior.
- [x] Limitar el cambio a sanitización, actualización documental y nombre de colección.
- [x] Mantener intactos `POST /v1/responses`, la autenticación Bearer y el contrato SSE.
- [ ] Crear un único commit neutral después de completar todas las validaciones.
- [ ] Evitar cambios funcionales adicionales hasta terminar la entrega.

## 3. Evidencia sanitizada

- [x] Sustituir referencias específicas por “plataforma cliente”, “cliente conversacional”, “proyecto de agente conversacional” u “organización cliente”, según el contexto.
- [x] Generalizar las preguntas de entrevista del corpus sin alterar su intención.
- [x] Actualizar los reportes JSON conservando intactas las métricas.
- [x] Confirmar mediante búsqueda insensible a mayúsculas que no existan coincidencias del nombre anterior en archivos rastreados.
- [x] Confirmar que ningún nombre de archivo rastreado contenga el nombre anterior.
- [ ] Guardar únicamente capturas y registros sin claves, encabezados de autorización ni transcripciones completas.

## 4. Índice RAG

- [x] Cambiar el valor predeterminado de `CHROMA_COLLECTION` a `agente_cv_v1` en el código y en `.env.example`.
- [x] Cambiar los metadatos internos de la colección a `agente_cv_rag`.
- [x] Mantener sin cambios el archivo `.env` y los secretos locales.
- [ ] Configurar `CHROMA_COLLECTION=agente_cv_v1` en Railway.
- [ ] Confirmar en los registros de despliegue que `scripts.ensure_index` crea o actualiza la nueva colección.
- [ ] Conservar temporalmente la colección anterior en el volumen para permitir rollback.
- [ ] Hacer una pregunta verificable y confirmar que la respuesta utiliza recuperación RAG correcta.

## 5. Pruebas finales

- [x] Ejecutar las 56 pruebas automatizadas.
- [x] Ejecutar `git diff --check`.
- [ ] Confirmar que `/health` devuelve HTTP `200` con `{"status":"ok"}`.
- [ ] Confirmar que `/docs`, `/redoc` y `/openapi.json` devuelven HTTP `404` en producción.
- [ ] Confirmar las cabeceras `Strict-Transport-Security`, `X-Content-Type-Options`, `Content-Security-Policy`, `X-Frame-Options` y `Referrer-Policy`.
- [ ] Confirmar HTTP `401` sin una credencial válida.
- [ ] Confirmar una solicitud autenticada desde la plataforma cliente.
- [ ] Confirmar que una conversación SSE termina con `response.completed` y `[DONE]`.

## 6. Despliegue

- [ ] Revisar el diff completo antes de confirmar los cambios.
- [ ] Crear el commit `docs: anonimiza referencias del cliente y prepara entrega`.
- [ ] Subir el commit a la rama de producción.
- [ ] Vigilar la construcción, el healthcheck y la reconstrucción de `agente_cv_v1`.
- [ ] Ejecutar el humo público de salud, documentación, cabeceras, autenticación, RAG y SSE.
- [ ] Confirmar que el repositorio queda limpio después del commit.

## 7. Rollback

Activar rollback si el servicio no inicia, el healthcheck falla, la nueva colección no se construye, RAG deja de recuperar información o el cliente conversacional deja de completar SSE.

1. Restaurar el deployment asociado al commit `9c5d333c814323a4440ed720e689169ad8c89a17`.
2. Restaurar en Railway el valor anterior de `CHROMA_COLLECTION`.
3. No eliminar ninguna colección del volumen durante la ventana de entrega.
4. Verificar `/health` y una conversación desde la plataforma cliente.
5. Registrar la causa sin incluir secretos ni transcripciones completas.

## 8. Monitoreo manual

Durante la entrega y las primeras horas de disponibilidad:

- Revisar errores de construcción e inicio.
- Revisar respuestas `401`, `413`, `429` y `5xx` sin registrar credenciales.
- Vigilar latencia, desconexiones SSE y errores del proveedor del modelo.
- Vigilar consumo de OpenAI y uso de recursos en Railway.
- Ejecutar periódicamente una consulta corta de RAG y una comprobación de `/health`.
- Mantener identificable el último deployment funcional.

## 9. Limitaciones conocidas

- El rate limiting vive en memoria, se reinicia al redesplegar y no se comparte entre réplicas.
- El despliegue controlado utiliza una sola instancia y no incorpora Redis.
- No existe un límite distribuido de concurrencia SSE ni un presupuesto diario automatizado.
- Chroma es embebido y depende del volumen persistente o de la reconstrucción desde las fuentes versionadas.
- El monitoreo inicial es manual; no se incorporan OpenTelemetry ni una plataforma adicional de observabilidad.
- La sanitización cubre la versión actual del repositorio, no el historial Git ni nombres de carpetas externas.

Estas limitaciones son aceptadas para la entrega inmediata porque el flujo real ya funcionó desde el cliente conversacional y no justifican una migración arquitectónica de último momento.
