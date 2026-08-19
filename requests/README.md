# Pruebas manuales de la API

Esta carpeta contiene solicitudes repetibles para comprobar el agente sin volver a escribir rutas, encabezados o cuerpos JSON.

## Estado actual

- `GET /health` puede ejecutarse desde ahora.
- `POST /v1/responses` acepta solicitudes de texto y devuelve una respuesta simulada no streaming.
- La autenticación Bearer ya está implementada. El RAG, el modelo y el streaming permanecen pendientes de integración al endpoint.
- Los cuerpos se basan en el contrato preliminar de `docs/contrato-open-responses.md`; deberán ajustarse si una solicitud real de Banorte utiliza otro subconjunto del contrato.

## Archivos

| Archivo | Propósito |
|---|---|
| `run.ps1` | Ejecuta por nombre cada prueba utilizando `curl.exe`. |
| `manual.http` | Muestra las solicitudes en formato HTTP para clientes compatibles. |
| `payloads/profile.json` | Pregunta válida con respuesta completa. |
| `payloads/unknown.json` | Pregunta cuya respuesta no está documentada. |
| `payloads/multiturn.json` | Transcripción stateless con una pregunta de seguimiento. |
| `payloads/privacy.json` | Solicitud de información privada que debe manejarse de forma segura. |
| `payloads/stream.json` | Solicitud con `stream: true`. |
| `payloads/malformed.json` | JSON intencionalmente inválido para comprobar errores. |

## Configuración local

Las claves no se guardan en esta carpeta. Configura las variables únicamente en la sesión local de PowerShell:

```powershell
$env:SERVICE_URL="http://127.0.0.1:8000"
$env:AGENT_BASE_URL="http://127.0.0.1:8000/v1"
$env:AGENT_API_KEY="tu-clave-local-del-agente"
```

`AGENT_API_KEY` es la clave con la que Banorte invocará el agente. Nunca debe contener `OPENAI_API_KEY`.

En Railway sólo cambiarán las URL y la clave de entrada:

```powershell
$env:SERVICE_URL="https://nombre-del-servicio.up.railway.app"
$env:AGENT_BASE_URL="https://nombre-del-servicio.up.railway.app/v1"
$env:AGENT_API_KEY="clave-configurada-en-banorte-y-railway"
```

## Ejecución

Desde la raíz del repositorio:

```powershell
.\requests\run.ps1 health
.\requests\run.ps1 profile
.\requests\run.ps1 unknown
.\requests\run.ps1 multiturn
.\requests\run.ps1 privacy
.\requests\run.ps1 no-auth
.\requests\run.ps1 bad-auth
.\requests\run.ps1 malformed
.\requests\run.ps1 stream
```

Para ver los casos disponibles:

```powershell
.\requests\run.ps1 help
```

## Resultados esperados

| Caso | Resultado esperado |
|---|---|
| `health` | HTTP `200` y JSON con `status: ok`. |
| `profile` | Actualmente HTTP `200`, `application/json` y respuesta simulada. La respuesta RAG queda pendiente. |
| `unknown` | Actualmente HTTP `200` con respuesta simulada. La política de incertidumbre queda pendiente de integración. |
| `multiturn` | Actualmente HTTP `200` con respuesta simulada. La comprensión del historial queda pendiente de integración. |
| `privacy` | Actualmente HTTP `200` con respuesta simulada. Los guardrails quedan pendientes de integración. |
| `no-auth` | HTTP `401` y encabezado `WWW-Authenticate: Bearer`. |
| `bad-auth` | HTTP `401` sin revelar la clave recibida ni la configurada. |
| `malformed` | HTTP `400` o `422`, según el contrato final, con error controlado. |
| `stream` | Actualmente HTTP `501`; SSE queda pendiente hasta confirmar que forma parte del alcance final. |

## Seguridad

- No escribas claves reales en `manual.http` ni en los JSON.
- No guardes encabezados `Authorization` en capturas o reportes.
- No confirmes en Git archivos de salida que contengan transcripciones completas.
- Antes de conservar evidencia, elimina credenciales, identificadores internos y datos privados.

## Criterio de terminado

La actividad estará terminada cuando todos los casos aplicables puedan ejecutarse con los comandos anteriores contra la API real, produzcan el resultado esperado y no requieran editar manualmente los cuerpos o encabezados.
