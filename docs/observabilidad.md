# Observabilidad y monitoreo operativo

## Alcance implementado

La aplicación incluye cuatro señales complementarias:

1. **Logs JSON:** eventos HTTP, seguridad, RAG, SSE y proveedor de IA.
2. **Métricas Prometheus:** contadores, gauges e histogramas en `GET /metrics`.
3. **Trazas distribuidas:** spans FastAPI, HTTPX, RAG y OpenAI exportados por
   OTLP/HTTP.
4. **Seguimiento de errores:** integración opcional con Sentry.

No se registran cuerpos HTTP, encabezados de autorización, transcripciones,
prompts, respuestas, consultas RAG ni fragmentos recuperados. La cardinalidad de
las etiquetas Prometheus se mantiene acotada; el identificador de solicitud y
los identificadores de trazas aparecen únicamente en logs y spans.

## Correlación

Cada solicitud recibe un identificador aleatorio y lo devuelve en
`X-Request-ID`. Si el cliente envía un `X-Request-ID` válido de hasta 128
caracteres ASCII seguros, se conserva. Los logs añaden:

- `request_id`;
- `trace_id` y `span_id` cuando OpenTelemetry está activo;
- ruta normalizada, método, código HTTP y duración completa;
- indicador de desconexión del cliente.

El mismo identificador se envía a OpenAI como `X-Client-Request-Id`. La
propagación W3C `traceparent` de las llamadas HTTP salientes se realiza mediante
la instrumentación de HTTPX.

## Variables

```text
LOG_LEVEL=INFO
LOG_JSON=true
METRICS_ENABLED=true
METRICS_API_KEY=clave_independiente_para_el_scraper

OTEL_ENABLED=true
OTEL_SERVICE_NAME=agente-cv
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://collector.example.com/v1/traces
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Bearer valor
OTEL_EXPORT_TIMEOUT_SECONDS=10
OTEL_TRACE_SAMPLE_RATIO=1.0

SENTRY_DSN=https://clave@organizacion.ingest.sentry.io/proyecto
SENTRY_TRACES_SAMPLE_RATE=0.0
```

`METRICS_API_KEY`, las cabeceras OTLP y `SENTRY_DSN` son secretos. No deben
guardarse en Git ni reutilizar `AGENT_API_KEY`. En producción, `/metrics`
responde `503` mientras no exista `METRICS_API_KEY`; en desarrollo puede
consultarse sin clave si la variable está vacía.

Sentry se usa inicialmente para errores. Su muestreo de transacciones permanece
en `0.0` porque OpenTelemetry es la fuente principal de trazas distribuidas. El
SDK se inicializa sin PII, sin cuerpos de solicitudes y sin variables locales.

## Métricas disponibles

| Familia | Propósito |
|---|---|
| `agent_http_requests_total` | Tráfico por método, ruta normalizada y estado |
| `agent_http_request_duration_seconds` | Latencia completa, incluido SSE |
| `agent_http_errors_total` | Errores `401`, `413`, `429` y `5xx` |
| `agent_sse_active_streams` | Conexiones SSE abiertas |
| `agent_sse_streams_total` | Streams completados, desconectados o con error |
| `agent_openai_requests_total` | Llamadas de generación y embeddings por resultado |
| `agent_openai_request_duration_seconds` | Latencia del proveedor |
| `agent_openai_tokens_total` | Tokens de entrada, salida, total, caché y razonamiento |
| `agent_rag_searches_total` | Búsquedas RAG correctas o fallidas |
| `agent_rag_search_duration_seconds` | Latencia de recuperación y reranking |
| `agent_rag_result_count` | Cantidad de fragmentos seleccionados |
| `agent_rag_top_score` | Mejor similitud coseno seleccionada |

El runtime de Prometheus agrega también métricas estándar de proceso y Python.

### Consulta local

```powershell
$Headers = @{ Authorization = "Bearer $env:METRICS_API_KEY" }
Invoke-WebRequest http://127.0.0.1:8000/metrics -Headers $Headers
```

## OpenTelemetry

La aplicación exporta trazas mediante OTLP sobre HTTP. El valor de
`OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` debe ser el endpoint final de trazas e
incluir `/v1/traces`.

Los spans manuales principales son:

- `rag.search`;
- `openai.embeddings.create`;
- `openai.responses.create`;
- `openai.responses.stream`.

La instrumentación FastAPI crea el span de servidor y HTTPX crea los spans de
cliente. `/health` y `/metrics` se excluyen de las trazas para evitar ruido.

El archivo `monitoring/otel-collector.example.yaml` sirve como base para un
OpenTelemetry Collector. Antes de usarlo, configura en el collector:

```text
OTEL_BACKEND_ENDPOINT=https://backend.example.com
OTEL_BACKEND_AUTHORIZATION=Bearer valor
```

Para probar solamente la recepción se puede eliminar temporalmente el exporter
`otlphttp/backend` y conservar `debug`.

## Prometheus, Grafana y alertas

- `monitoring/prometheus/prometheus.example.yml`: scrape autenticado de
  `/metrics` y verificación externa de `/health` mediante Blackbox Exporter.
- `monitoring/prometheus/blackbox.yml`: módulo HTTPS para disponibilidad.
- `monitoring/prometheus/alerts.yml`: reglas de disponibilidad, errores `5xx`,
  latencia, `429`, OpenAI, SSE y ausencia de resultados RAG.
- `monitoring/grafana/agent-observability.json`: tablero importable en Grafana.

Antes de iniciar Prometheus:

1. Sustituye `service.example.com` por el host real.
2. Guarda la clave de métricas fuera del repositorio en el archivo indicado por
   `credentials_file`.
3. Valida las reglas con `promtool check rules alerts.yml`.
4. Conecta Prometheus con Alertmanager para entregar notificaciones.
5. Importa el JSON en Grafana y selecciona el datasource Prometheus.

## Disponibilidad automática en Google Cloud

`monitoring/gcp` contiene Terraform para crear:

- una verificación pública HTTPS de `GET /health` cada minuto;
- comprobación del contenido `"status":"ok"`;
- registro de probes fallidos;
- una alerta crítica después de dos minutos de fallos.

El módulo no crea canales de notificación porque éstos suelen ser recursos
compartidos. Recibe los nombres completos de canales ya existentes.

```powershell
Set-Location monitoring/gcp
terraform init
terraform plan `
  -var="project_id=mi-proyecto" `
  -var="service_host=mi-servicio.run.app" `
  -var='notification_channel_names=["projects/mi-proyecto/notificationChannels/123"]'
terraform apply
```

Si todavía no existe un canal, puede dejarse la lista vacía para crear primero
la verificación y asociar el canal más tarde. Se requieren permisos para editar
uptime checks y políticas de Cloud Monitoring.

Cloud Run ya publica métricas de infraestructura como solicitudes, latencia,
CPU, memoria e instancias. Las métricas específicas del agente requieren un
scraper Prometheus o una canalización administrada adicional.

## Activación en el despliegue actual

1. Define `METRICS_API_KEY` y confirma que `/metrics` responde `200` únicamente
   con esa credencial.
2. Crea o selecciona un backend compatible con OTLP.
3. Define `OTEL_ENABLED=true`, el endpoint y sus cabeceras secretas.
4. Mantén `OTEL_TRACE_SAMPLE_RATIO=1.0` durante la validación; tras observar el
   volumen, bájalo a `0.1`–`0.25` si el costo lo exige.
5. Define `SENTRY_DSN` si se utilizará el tablero de errores.
6. Despliega y realiza una respuesta JSON, una SSE y una consulta que active el
   RAG.
7. Confirma que los tres recorridos comparten `request_id`/`trace_id` y que no
   contienen texto conversacional.
8. Configura el scraper y las notificaciones externas. El código por sí solo no
   puede avisar si todo el servicio deja de ejecutarse; por eso la verificación
   de disponibilidad debe vivir fuera del contenedor.

## Referencias técnicas

- [OpenTelemetry para FastAPI](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html)
- [Cliente Prometheus para ASGI](https://prometheus.github.io/client_python/exporting/http/asgi/)
- [Monitoreo de Cloud Run](https://cloud.google.com/run/docs/monitoring)
- [Uptime checks de Cloud Monitoring](https://cloud.google.com/monitoring/uptime-checks)
- [OpenAI: request IDs y depuración](https://developers.openai.com/api/reference/overview#debugging-requests)
