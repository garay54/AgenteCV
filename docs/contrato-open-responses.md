# Contrato de integración Open Responses — Agente de CV Banorte

## 1. Propósito

Este documento define el contrato externo entre la plataforma del Reto IA Banorte y el agente de CV. Su objetivo es establecer qué URL invoca Banorte, qué encabezados y cuerpo envía, qué respuestas debe devolver el agente, cómo se transmite el historial, cómo funciona el streaming y cómo se representan los errores.

Este documento no define la implementación interna del agente, el proveedor del modelo, el framework web, el almacenamiento del conocimiento ni la arquitectura RAG.

## 2. Estado

| Actividad | Estado | Motivo |
|---|---|---|
| R06 — Confirmar contrato Open Responses | En progreso | Banorte confirmó en una solicitud real que utiliza `stream: true`; la implementación local ya emite SSE, pero falta que la plataforma acepte la secuencia desplegada. |
| R07 — Confirmar entrega del historial | Confirmado | La plataforma permite reproducir la transcripción o utilizar `previous_response_id`; para el MVP se seleccionó reproducir la transcripción. |
| R08 — Confirmar autenticación de entrada | Confirmado | La plataforma puede enviar una clave mediante `Authorization: Bearer <API_KEY>`. |

## 3. Fuentes

- Instrucciones originales del Reto IA Banorte.
- Formulario **Añadir un agente** de la plataforma de Banorte.
- [Especificación Open Responses](https://www.openresponses.org/specification).
- [Referencia Open Responses](https://www.openresponses.org/reference).
- [Esquema OpenAPI](https://www.openresponses.org/openapi/openapi.json).
- [Pruebas oficiales de aceptación](https://www.openresponses.org/compliance).

La versión de referencia observada en el esquema OpenAPI es `2026-04-24`. Falta confirmar si Banorte evalúa esa versión completa o un subconjunto del protocolo.

## 4. Configuración confirmada en Banorte

| Elemento | Comportamiento confirmado |
|---|---|
| URL registrada | Banorte solicita una URL base. |
| Ruta invocada | Las solicitudes se envían a `{URL base}/responses`. |
| API key | Campo opcional en el formulario. |
| Envío de API key | `Authorization: Bearer <API_KEY>`. |
| Modelo | Campo opcional. |
| Instrucciones | Banorte puede enviar instrucciones del sistema con cada solicitud. |
| Parámetros adicionales | Banorte permite añadir parámetros al cuerpo mediante un objeto JSON. |
| Estado de conversación | `Reproducir transcripción (sin estado)` o `previous_response_id (el agente guarda el estado)`. |
| Modalidad del MVP | Texto. Las entradas de imágenes y archivos permanecerán desactivadas. |
| Cliente conversacional | Banorte proporciona el chat, permite seleccionar el agente y envía las solicitudes al endpoint registrado. No se requiere frontend propio para el MVP. |
| Streaming observado | Una solicitud real de Banorte envió `stream: true`; por ello SSE es obligatorio para la integración. |

La función de importar una tarjeta de agente desde `/.well-known/agent-card.json` es opcional y no forma parte del contrato mínimo del MVP.

El agente Guía consultado confirmó que sus ejemplos de `POST /v1/responses` describían llamadas desde un backend hacia un proveedor de modelos, no el payload exacto enviado por Banorte. Por tanto, esos ejemplos no se utilizarán como evidencia del contrato externo.

## 5. Endpoint HTTP

### 5.1 URL

La URL pública deberá usar HTTPS. La plataforma agrega `/responses` a la URL base registrada.

Ejemplo:

```text
URL base registrada: https://agente.example.com/v1
Endpoint invocado:   https://agente.example.com/v1/responses
```

### 5.2 Método

```http
POST /v1/responses
```

### 5.3 Encabezados de solicitud

```http
Content-Type: application/json
Authorization: Bearer <API_KEY>
```

- `Content-Type: application/json` corresponde al requisito normativo de la especificación.
- `Authorization` se exigirá cuando el agente se registre con una API key.
- La clave real nunca deberá aparecer en este documento, el repositorio, ejemplos o registros.

### 5.4 Encabezados de respuesta

| Modalidad | `Content-Type` esperado |
|---|---|
| No streaming | `application/json` |
| Streaming | `text/event-stream` |

## 6. Solicitud de creación de respuesta

La especificación permite que `input` sea un texto o un arreglo de items. Para conversaciones, el formato esperado es un arreglo de mensajes.

Campos relevantes para el MVP:

| Campo | Uso esperado |
|---|---|
| `input` | Pregunta actual y transcripción de la conversación. |
| `model` | Identificador opcional enviado desde la configuración de Banorte. |
| `instructions` | Instrucciones opcionales configuradas en la plataforma. |
| `stream` | Solicita respuesta completa o transmisión incremental. |
| `previous_response_id` | No se utilizará con el modo de reproducción de transcripción. |
| Parámetros adicionales | Valores JSON configurados por Mario en el formulario del agente. |

### 6.1 Ejemplo de referencia no streaming

El siguiente ejemplo se basa en la especificación, pero todavía no constituye evidencia de aceptación por Banorte:

```json
{
  "model": "cv-agent",
  "input": [
    {
      "type": "message",
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "¿Cuál es la experiencia profesional de Mario?"
        }
      ]
    }
  ],
  "stream": false
}
```

### 6.2 Ejemplo de referencia streaming

```json
{
  "model": "cv-agent",
  "input": [
    {
      "type": "message",
      "role": "user",
      "content": "Resume el perfil profesional de Mario."
    }
  ],
  "stream": true
}
```

### 6.3 Validaciones mínimas de entrada

- El cuerpo debe ser JSON válido.
- `input` debe tener un tipo aceptado por la especificación.
- Cada item estructurado debe indicar un `type` válido.
- Los mensajes deben contener un rol y contenido válidos.
- Los parámetros desconocidos o no soportados deben producir un comportamiento documentado.
- Las solicitudes que excedan los límites configurados deben ser rechazadas de forma controlada.

## 7. Respuesta no streaming

Una solicitud con `stream: false` deberá devolver HTTP 200, `Content-Type: application/json` y un objeto `ResponseResource` válido.

El esquema OpenAPI `2026-04-24` declara los siguientes campos en el objeto de respuesta:

```text
id, object, created_at, completed_at, status, incomplete_details,
model, previous_response_id, instructions, output, error, tools,
tool_choice, truncation, parallel_tool_calls, text, top_p,
presence_penalty, frequency_penalty, top_logprobs, temperature,
reasoning, usage, max_output_tokens, max_tool_calls, store,
background, service_tier, metadata, safety_identifier,
prompt_cache_key
```

Algunos campos pueden contener `null`, pero el resultado final deberá validarse contra el esquema oficial y las pruebas de aceptación.

### 7.1 Ejemplo de referencia

Este ejemplo es un borrador para la implementación. Deberá sustituirse o confirmarse con una respuesta aceptada por Banorte:

```json
{
  "id": "resp_example_001",
  "object": "response",
  "created_at": 1786946400,
  "completed_at": 1786946401,
  "status": "completed",
  "incomplete_details": null,
  "model": "cv-agent",
  "previous_response_id": null,
  "instructions": null,
  "output": [
    {
      "id": "msg_example_001",
      "type": "message",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Mario cuenta con experiencia profesional en...",
          "annotations": []
        }
      ]
    }
  ],
  "error": null,
  "tools": [],
  "tool_choice": "auto",
  "truncation": "disabled",
  "parallel_tool_calls": false,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "top_p": 1,
  "presence_penalty": 0,
  "frequency_penalty": 0,
  "top_logprobs": 0,
  "temperature": 1,
  "reasoning": null,
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens_details": {
      "reasoning_tokens": 0
    }
  },
  "max_output_tokens": null,
  "max_tool_calls": null,
  "store": false,
  "background": false,
  "service_tier": "default",
  "metadata": {},
  "safety_identifier": null,
  "prompt_cache_key": null
}
```

## 8. Streaming SSE

Una solicitud con `stream: true` deberá responder con `Content-Type: text/event-stream`.

Reglas confirmadas por la especificación:

- Cada evento debe incluir un campo SSE `event`.
- El valor de `event` debe coincidir con el campo `type` del objeto enviado en `data`.
- `data` debe contener un objeto JSON para los eventos normales.
- Los eventos deben conservar un `sequence_number` ordenado.
- El cierre del stream debe enviar la cadena literal `[DONE]`.
- No se debe utilizar el campo SSE `id`.

Flujo esperado para una respuesta de texto:

```text
response.created
response.in_progress
response.output_item.added
response.content_part.added
response.output_text.delta        (uno o más)
response.output_text.done
response.content_part.done
response.output_item.done
response.completed
[DONE]
```

Ejemplo abreviado:

```text
event: response.output_text.delta
data: {"type":"response.output_text.delta","sequence_number":4,"item_id":"msg_example_001","output_index":0,"content_index":0,"delta":"Mario"}

event: response.completed
data: {"type":"response.completed","sequence_number":9,"response":{"id":"resp_example_001","object":"response","status":"completed"}}

data: [DONE]
```

El ejemplo está abreviado y no reemplaza los eventos completos definidos en el esquema OpenAPI.

La implementación local fue validada con una llamada real a `gpt-5.6-luna`: devolvió HTTP 200, `text/event-stream`, números de secuencia monotónicos, texto incremental, `response.completed` y el terminador `[DONE]`. La aceptación de esta secuencia desde la interfaz de Banorte permanece pendiente hasta desplegar el cambio.

## 9. Historial de conversación

### 9.1 Configuración seleccionada

```text
Reproducir transcripción (sin estado)
```

### 9.2 Responsabilidades

- Banorte administra la conversación y vuelve a enviar la transcripción necesaria en cada solicitud.
- El agente procesa el historial recibido como parte de `input`.
- El agente no necesita almacenar conversaciones entre solicitudes.
- El agente no utilizará `previous_response_id` en el MVP.

### 9.3 Validación pendiente

Se deberá ejecutar una conversación de varios turnos y comprobar que la segunda solicitud contiene información suficiente de los mensajes anteriores.

## 10. Autenticación

### 10.1 Mecanismo confirmado

```http
Authorization: Bearer <API_KEY>
```

### 10.2 Comportamiento esperado

| Caso | Resultado esperado |
|---|---|
| Clave válida | La solicitud continúa. |
| Encabezado ausente | HTTP 401. |
| Formato incorrecto | HTTP 401. |
| Clave incorrecta | HTTP 401. |

La clave utilizada para autenticar a Banorte debe ser diferente de cualquier credencial utilizada con el proveedor del modelo.

## 11. Errores

Formato general:

```json
{
  "error": {
    "message": "Descripción comprensible del error.",
    "type": "invalid_request",
    "param": "input",
    "code": "invalid_input"
  }
}
```

Errores definidos por la especificación:

| Tipo | Código HTTP |
|---|---:|
| `invalid_request` | 400 |
| `not_found` | 404 |
| `too_many_requests` | 429 |
| `server_error` | 500 |
| `model_error` | 500 |

Los errores de autenticación se manejarán como HTTP 401. Durante streaming, un evento `error` deberá ser seguido por `response.failed` y el cierre correspondiente del stream.

## 12. Archivos e imágenes

El agente Guía observado sólo admite texto. El formulario permite habilitar entradas de imágenes y archivos para agentes personalizados, pero estas capacidades permanecerán desactivadas en el MVP.

Por tanto:

- No se requiere recibir imágenes.
- No se requiere recibir archivos.
- No se requiere devolver archivos.
- La configuración **Entrega de archivos** no aplica al MVP.

## 13. Aspectos pendientes de confirmar mediante pruebas

- Cuerpo JSON exacto enviado por Banorte.
- Forma exacta en que Banorte reproduce la transcripción dentro de `input`.
- Inclusión u omisión del campo `model`.
- Inclusión de `instructions` y parámetros adicionales.
- Aceptación por Banorte de la secuencia SSE implementada y desplegada.
- Confirmación de si la interfaz consume todo el ciclo semántico o sólo un subconjunto de eventos.
- Versión o subconjunto de Open Responses utilizado en la evaluación.
- Tiempo máximo de respuesta.
- Tamaño máximo de solicitud.
- Límites de frecuencia.
- Formato exacto mostrado por Banorte ante errores.

## 14. Evidencias requeridas

Las evidencias deberán guardarse sin secretos ni datos sensibles:

```text
docs/evidencias/
├── r07-estado-conversacion.png
├── r08-autenticacion-bearer.png
└── r06-integracion-banorte.md

docs/ejemplos-open-responses/
├── request-non-stream.json
├── response-non-stream.json
├── request-stream.json
├── response-stream.txt
├── error-400.json
├── error-401.json
└── error-500.json
```

Los ejemplos reales se crearán después de recibir solicitudes desde Banorte. No deben contener API keys, encabezados sensibles ni información privada.

## 15. Criterios para cerrar R06

R06 podrá marcarse como completada cuando:

- Exista una solicitud no streaming recibida desde Banorte.
- Exista una respuesta no streaming aceptada y mostrada correctamente.
- Exista una secuencia SSE desplegada, aceptada y finalizada correctamente desde Banorte.
- Se hayan probado errores representativos.
- Los ejemplos sanitizados estén guardados en el proyecto.
- La respuesta se haya validado contra el esquema OpenAPI aplicable.
- Se hayan ejecutado las pruebas de aceptación correspondientes al alcance del reto.

## 16. Observaciones sobre la especificación

- La sección normativa indica que las solicitudes deben enviarse como `application/json`, mientras que la referencia también menciona `application/x-www-form-urlencoded`. Para este proyecto se documenta JSON como formato requerido y se verificará el comportamiento real de Banorte.
- El esquema OpenAPI marca numerosos campos del objeto de respuesta como obligatorios, aunque algunos ejemplos narrativos omiten campos anulables. La validación automática del esquema y las pruebas de aceptación tendrán prioridad sobre los ejemplos abreviados.
- La autenticación aparece como obligatoria en la especificación, pero el formulario de Banorte presenta la API key como opcional. El agente podrá registrarse con una clave Bearer para eliminar esa ambigüedad.
- WebSockets y `/responses/compact` aparecen en la versión `2026-04-24`, pero no se consideran parte del MVP hasta que Banorte confirme que los evalúa.

## 17. Historial de cambios

| Fecha | Cambio | Responsable |
|---|---|---|
| 2026-08-17 | Creación inicial con información de la especificación y del formulario de Banorte. | Mario |
