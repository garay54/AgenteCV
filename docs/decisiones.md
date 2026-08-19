# Decisiones técnicas

## D01. Lenguaje y framework de la API

**Estado:** Aceptada  
**Fecha:** 2026-08-18

### Contexto

El proyecto requiere implementar una API pública compatible con Open Responses, integrar un agente basado en un modelo de lenguaje e incorporar recuperación y evaluación RAG.

Se compararon Python con FastAPI y JavaScript con Express considerando experiencia previa, velocidad de implementación, validación, procesamiento asíncrono, disponibilidad de librerías y facilidad de operación.

### Decisión

Se utilizarán **Python y FastAPI** para implementar la API del agente.

### Razones

- Existe experiencia práctica demostrable utilizando Python.
- Python permite implementar la API, el procesamiento documental, el RAG y su evaluación dentro del mismo ecosistema.
- FastAPI permite validar solicitudes y respuestas mediante modelos de datos.
- FastAPI genera documentación OpenAPI automáticamente.
- Soporta operaciones asíncronas para llamadas al modelo de lenguaje y otros servicios externos.
- Python dispone de librerías maduras para embeddings, recuperación de información, procesamiento de documentos y evaluación de sistemas RAG.
- Mantener un solo lenguaje reduce el esfuerzo de integración durante el reto.

### Alternativa considerada

Se consideró JavaScript con Express por su flexibilidad, soporte asíncrono y ecosistema web. No fue seleccionado porque ofrece menos ventajas para las tareas de RAG previstas y existe menor evidencia de experiencia práctica con JavaScript en la información profesional disponible.

### Consecuencias

- La API y el sistema RAG se desarrollarán en Python.
- Los modelos de entrada y salida deberán representar correctamente el contrato Open Responses.
- La documentación automática de FastAPI servirá como apoyo para pruebas, pero no sustituirá las pruebas de compatibilidad con la plataforma de Banorte.
- Las operaciones que esperen servicios externos podrán ser asíncronas.
- Las tareas intensivas de procesamiento no deberán ejecutarse directamente como si fueran operaciones asíncronas de red.

### Condición de revisión

La decisión solamente se reconsiderará si la plataforma de Banorte presenta una incompatibilidad comprobada con FastAPI/Python o si aparece un requisito obligatorio exclusivo del ecosistema JavaScript.

## D02. Proveedor y modelo de inteligencia artificial

**Estado:** Aceptada  
**Fecha:** 2026-08-18

### Contexto

El agente necesita un modelo de lenguaje capaz de responder en español a partir del contexto recuperado por el sistema RAG. Para la demostración se priorizan la estabilidad, la disponibilidad de cuota, el tiempo de respuesta, el costo y la compatibilidad con streaming, además de la calidad de las respuestas.

Se compararon OpenAI con `gpt-4o-mini` y Anthropic con `claude-haiku-4-5-20251001`.

### Comparación

| Criterio | OpenAI: `gpt-4o-mini` | Anthropic: `claude-haiku-4-5-20251001` |
|---|---|---|
| Calidad para el caso de uso | Adecuada para tareas enfocadas; pendiente de validar con preguntas reales | Modelo rápido con capacidad multilingüe; pendiente de validar con preguntas reales |
| Latencia | Modelo clasificado como rápido; se medirá con el agente | Modelo clasificado como el más rápido de la familia Claude; se medirá con el agente |
| Costo por millón de tokens | USD $0.15 de entrada y USD $0.60 de salida | USD $1.00 de entrada y USD $5.00 de salida |
| Límites | Dependen del nivel de uso de la cuenta | Dependen del nivel y antigüedad de la cuenta |
| Disponibilidad regional | Disponible en México | Disponible en México |
| Idioma | Se validará la calidad de las respuestas en español | Anthropic declara capacidad multilingüe; se validará la calidad en español |
| Streaming | Compatible | Compatible mediante SSE |
| Integración | Compatible con Responses API; requiere exponer el contrato Open Responses desde la aplicación | Requiere adaptar Messages API y sus eventos al contrato Open Responses |

### Decisión

- **Proveedor principal:** OpenAI.
- **Modelo principal:** `gpt-4o-mini`.
- **Proveedor de contingencia:** Anthropic.
- **Modelo de contingencia:** `claude-haiku-4-5-20251001`.

### Razones

- `gpt-4o-mini` tiene el menor costo de los dos candidatos.
- Es compatible con streaming y con Responses API, lo cual reduce el esfuerzo de adaptación interno.
- Sus límites documentados son suficientes para el desarrollo y la demostración, sujetos a la cuota efectiva de la cuenta.
- Haiku 4.5 ofrece una contingencia independiente frente a indisponibilidad, timeout o agotamiento de cuota de OpenAI.
- El presupuesto previsto de USD $5 en Anthropic es suficiente para probar y mantener la contingencia durante el reto.
- La selección no depende únicamente de la capacidad declarada de los modelos; deberá validarse con preguntas reales del banco de evaluación.

### Activación de la contingencia

La aplicación podrá recurrir a Anthropic cuando el proveedor principal presente un timeout, un error temporal, indisponibilidad o agotamiento de cuota. Una pregunta difícil, una recuperación RAG insuficiente o la ausencia de información no deberán activar automáticamente la contingencia.

### Validación pendiente

Antes de la demostración se ejecutará el mismo conjunto de preguntas en ambos modelos para comparar corrección, alucinaciones, manejo de incertidumbre, calidad del español, tiempo hasta el primer fragmento, tiempo total, consumo, errores y funcionamiento del streaming.

Si la cuenta de OpenAI no dispone de una clave funcional y cuota suficiente, se revisará el orden de los proveedores, ya que un proveedor sin acceso confirmado no puede operar como principal.

### Referencias

- [OpenAI: GPT-4o mini](https://developers.openai.com/api/docs/models/gpt-4o-mini)
- [Anthropic: modelos Claude](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Anthropic: precios](https://platform.claude.com/docs/en/about-claude/pricing)
- [Anthropic: streaming](https://platform.claude.com/docs/en/build-with-claude/streaming)

## D03. SDK de proveedores y capa de adaptación

**Estado:** Aceptada  
**Fecha:** 2026-08-18

### Contexto

La API pública debe cumplir el contrato Open Responses, mientras que OpenAI y Anthropic utilizan formatos, objetos de respuesta y eventos de streaming particulares. La implementación también debe permitir cambiar de proveedor o activar la contingencia sin modificar la ruta pública, el RAG ni la lógica conversacional.

Se compararon las siguientes alternativas:

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Utilizar directamente los SDK oficiales | Mayor velocidad de desarrollo y soporte nativo para las funciones de cada proveedor | Acopla la aplicación a sus formatos particulares |
| Implementar clientes HTTP propios | Ofrece control explícito sobre solicitudes, respuestas y eventos | Requiere más código, pruebas y mantenimiento |
| Utilizar los SDK oficiales detrás de adaptadores propios | Combina velocidad de desarrollo con desacoplamiento entre proveedores | Requiere mantener una pequeña capa adicional |

### Decisión

Se utilizarán los SDK oficiales de OpenAI y Anthropic detrás de adaptadores propios que implementen una interfaz interna común.

No se implementarán inicialmente clientes HTTP manuales para comunicarse con los proveedores.

La API pública conservará el contrato Open Responses y no expondrá directamente los objetos, respuestas o errores particulares de los SDK.

### Capa de adaptación

El flujo general será:

```text
Plataforma Banorte
        │
        │ Open Responses
        ▼
POST /responses
        │
        ▼
Solicitud interna normalizada
        │
        ├── OpenAIProvider
        │      └── SDK oficial de OpenAI
        │
        └── AnthropicProvider
               └── SDK oficial de Anthropic
        │
        ▼
Respuesta o eventos internos normalizados
        │
        ▼
Respuesta o eventos Open Responses
```

La capa de adaptación tendrá las siguientes responsabilidades:

- Traducir las solicitudes Open Responses al formato interno del agente.
- Traducir el formato interno al formato requerido por cada proveedor.
- Ejecutar solicitudes normales y solicitudes con streaming mediante el SDK correspondiente.
- Normalizar texto, consumo de tokens, motivo de finalización y errores.
- Convertir los eventos particulares de cada proveedor en eventos internos comunes.
- Convertir la respuesta y los eventos internos al contrato Open Responses.
- Permitir seleccionar el proveedor principal o el proveedor de contingencia sin cambiar la ruta pública.

### Interfaz conceptual

La interfaz común deberá ofrecer, como mínimo, operaciones equivalentes a:

```text
generate(request) -> response
stream(request) -> secuencia de eventos
```

El formato interno contemplará solamente las capacidades necesarias para el MVP:

- Mensajes e historial.
- Instrucciones del sistema.
- Contexto recuperado por RAG.
- Indicación de streaming.
- Límite de salida.
- Texto generado.
- Consumo de tokens.
- Motivo de finalización.
- Errores normalizados.

### Consecuencias

- La ruta `/responses` no dependerá directamente de OpenAI ni de Anthropic.
- El cambio de proveedor se concentrará en la selección del adaptador.
- Incorporar otro proveedor requerirá implementar un nuevo adaptador, sin cambiar el contrato público.
- Las diferencias que no sean necesarias para el MVP no se intentarán normalizar inicialmente.
- La compatibilidad con Open Responses deberá validarse independientemente de que los SDK funcionen correctamente.

### Condición de revisión

Se considerará un cliente HTTP propio únicamente si un SDK oficial impide cumplir una parte obligatoria del contrato, no expone los eventos necesarios, introduce una incompatibilidad comprobada o dificulta de manera material el cambio de proveedor.

## D04. Estrategia de contexto: RAG ligero con conocimiento curado

**Estado:** Aceptada  
**Fecha:** 2026-08-18

### Contexto

El agente debe responder preguntas sobre la trayectoria profesional, formación e investigación con información verificable. Las fuentes disponibles incluyen documentos estructurados del perfil, dos tesis extensas y artículos científicos. Aunque RAG no aparece como una tecnología obligatoria en las instrucciones generales, fue indicado como tema técnico durante el proceso y Mario decidió utilizarlo y evaluarlo como parte central de su solución.

Indexar las tesis y publicaciones completas incorporaría información poco útil para el objetivo del agente, como revisiones bibliográficas, teoría general y referencias a contribuciones de otros autores. Esto podría provocar que la recuperación priorice fragmentos que no describen la experiencia o las aportaciones propias.

Se compararon las siguientes alternativas:

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Contexto completo dentro del prompt | Implementación sencilla y sin recuperación | Aumenta el contexto enviado en cada solicitud y no permite demostrar ni evaluar RAG |
| RAG sobre documentos originales completos | Conserva el máximo detalle disponible | Introduce ruido, dificulta distinguir aportaciones propias y puede recuperar información irrelevante |
| RAG ligero sobre documentos curados | Prioriza hechos profesionales y académicos relevantes, permite controlar las fuentes y facilita la evaluación | Requiere preparar y mantener resúmenes derivados de las fuentes originales |

### Decisión

Se implementará un **RAG ligero basado en conocimiento curado**.

El prompt fijo contendrá únicamente:

- El rol y propósito del agente.
- Las políticas de privacidad, alcance e incertidumbre.
- Las reglas para utilizar la evidencia recuperada.
- Un resumen profesional breve, si resulta necesario para mantener la identidad del agente.

Los detalles sobre experiencia, proyectos, habilidades, educación, tesis y publicaciones se obtendrán mediante recuperación semántica desde documentos Markdown sanitizados y verificados.

### Fuentes incluidas en el índice

El corpus inicial podrá incluir:

- `knowledge/profile.md`
- `knowledge/experience.md`
- `knowledge/projects.md`
- `knowledge/skills.md`
- `knowledge/publications.md`
- `knowledge/research.md`

Cada resumen de investigación deberá conservar, cuando la fuente lo permita:

- Problema y objetivo.
- Aportación personal.
- Metodología, modelos, algoritmos y tecnologías.
- Experimentos, resultados y métricas verificables.
- Decisiones, dificultades, limitaciones y aprendizajes relevantes.
- Relación con artículos o proyectos.
- Referencia a la fuente original utilizada para verificarlo.

### Fuentes excluidas del índice

No formarán parte del índice de producción:

- Las tesis y publicaciones completas de `FuenteDeVerdad/` y `FuenteDeVerdad_md/`.
- Documentos originales que contengan información privada.
- `knowledge/question_bank.md`, que se reservará para evaluación.
- `knowledge/open_questions.md`, mientras contenga información no confirmada.
- `knowledge/faq.md`, que se utilizará como referencia conversacional y apoyo para pruebas, pero no como fuente recuperable.
- README, decisiones, riesgos, cronogramas y demás documentación administrativa.

Los documentos originales se conservarán como fuentes privadas de verificación y para corregir o ampliar los documentos curados, pero no serán consultados directamente por el agente en producción.

### Consecuencias

- El agente demostrará recuperación semántica sin indexar material que no contribuya directamente a representar la trayectoria.
- Los resúmenes no se considerarán una reproducción completa de las fuentes; su suficiencia deberá comprobarse mediante evaluación.
- Si una pregunta relevante no puede responderse por falta de detalle, se ampliará el documento curado correspondiente con información verificada, en lugar de incorporar automáticamente la fuente completa.
- Excluir `knowledge/faq.md` reducirá la recuperación de respuestas duplicadas y favorecerá el uso de los hechos canónicos.
- La fragmentación de `knowledge/research.md` deberá conservar en los metadatos el título de la investigación, nivel académico, sección e identificador de fuente.
- La selección del modelo de embeddings, almacén vectorial, estrategia de fragmentación y parámetros de recuperación se documentará en decisiones posteriores.

### Criterio de validación

La decisión se considerará validada cuando una evaluación separada de recuperación y generación demuestre que:

- Las preguntas representativas recuperan fragmentos pertinentes del documento correcto.
- Las respuestas se apoyan en evidencia recuperada y no atribuyen como propias contribuciones de terceros.
- Las preguntas sin evidencia suficiente producen una declaración explícita de incertidumbre.
- Los fallos encontrados pueden corregirse ampliando o ajustando el conocimiento curado sin tener que indexar las tesis completas.

## D04.1. Fragmentación, embeddings y almacenamiento vectorial

**Estado:** Aceptada para el MVP; parámetros sujetos a evaluación  
**Fecha:** 2026-08-18

### Contexto

Después de seleccionar un RAG ligero faltaba definir cómo dividir los documentos, representar los fragmentos, almacenarlos y seleccionar los resultados. La configuración debe conservar la estructura del conocimiento, ser reproducible y permitir corregir el corpus sin entrenar nuevamente el modelo de lenguaje.

### Decisión

- La fragmentación respetará los encabezados Markdown y no combinará empleos, proyectos, publicaciones ni investigaciones diferentes.
- Los fragmentos tendrán un objetivo aproximado de 150 a 350 tokens y un máximo de 450 tokens.
- Se utilizará solapamiento de 50 tokens únicamente cuando una sección deba dividirse por superar el máximo. No se añadirá solapamiento entre secciones independientes.
- Cada fragmento conservará documento, título, tipo, ruta de sección, identificadores de fuente, nivel académico e identificador estable.
- El modelo inicial de embeddings será `text-embedding-3-small` de OpenAI.
- El almacén inicial será Chroma persistente y embebido, con distancia coseno. El índice será reconstruible desde los seis archivos autorizados.
- La búsqueda solicitará hasta 16 candidatos, devolverá cuatro resultados y limitará la salida a un máximo de dos fragmentos por documento.
- No se incorporará reranking en la primera versión. Sólo se añadirá si la evaluación muestra fallos que no se resuelvan mediante corpus, fragmentación o parámetros de búsqueda.
- No se fijará un umbral mínimo de similitud antes de observar la distribución de puntuaciones reales.

### Criterios de aceptación iniciales

- `Hit@3` por documento esperado: al menos 90 %.
- Documento esperado en `Top-1`: al menos 75 %.
- Cero fragmentos procedentes de documentos excluidos.
- Máximo de dos resultados del mismo documento entre los cuatro entregados.
- Registro por caso de consulta, resultados, puntuaciones, fuentes, latencia y error.

### Alternativas y revisión

`text-embedding-3-large`, un almacén administrado y un reranker quedan como alternativas. Sólo se adoptarán si aportan una mejora medible que justifique su costo o complejidad. Chroma embebido es suficiente para desarrollo y demostración local; su persistencia en la plataforma de despliegue deberá revisarse antes de publicar el servicio.

### Referencias

- [OpenAI: text-embedding-3-small](https://developers.openai.com/api/docs/models/text-embedding-3-small)
- [OpenAI: crear embeddings](https://developers.openai.com/api/reference/resources/embeddings/methods/create)
- [Chroma: configuración de colecciones](https://docs.trychroma.com/docs/collections/configure)

## D05. Manejo del estado conversacional

**Estado:** Aceptada para el MVP; pendiente de validación con una solicitud real de Banorte  
**Fecha:** 2026-08-18

### Contexto

La plataforma de Banorte permite seleccionar entre reproducir la transcripción completa en cada solicitud o utilizar `previous_response_id` para que el agente conserve el estado. En la configuración observada se seleccionó **Reproducir transcripción (sin estado)**.

El agente necesita mantener continuidad entre preguntas relacionadas, pero no requiere conservar conversaciones después de responder ni compartirlas entre solicitudes mediante almacenamiento propio.

### Decisión

El servicio será **stateless** respecto de la conversación.

- Banorte deberá enviar en cada solicitud la transcripción o los mensajes necesarios para reconstruir el contexto conversacional.
- La aplicación normalizará y utilizará ese historial únicamente en memoria mientras procesa la solicitud.
- El estado temporal comenzará al recibir la solicitud y terminará al entregar la respuesta completa o cerrar la transmisión correspondiente.
- Después de responder, el servidor descartará mensajes, contexto recuperado y respuesta temporal.
- El MVP no utilizará `previous_response_id`.
- El MVP no incorporará una base de datos, caché ni almacenamiento de sesiones conversacionales.
- Los registros operativos no deberán guardar transcripciones completas ni información profesional sensible innecesaria.

### Ubicación y duración del estado

| Elemento | Ubicación | Duración |
|---|---|---|
| Historial conversacional | Cuerpo de la solicitud enviado por Banorte y memoria del proceso | Sólo durante la solicitud |
| Fragmentos recuperados | Memoria del proceso | Sólo durante la solicitud |
| Respuesta en construcción | Memoria del proceso | Hasta completar o cerrar la respuesta |
| Conocimiento profesional | Índice RAG de Chroma | Persistente y reconstruible; no constituye estado conversacional |
| Configuración del agente | Variables de entorno y archivos autorizados | Durante la ejecución o hasta una nueva versión |

### Consecuencias

- Cualquier instancia disponible podrá atender una solicitud sin consultar sesiones creadas por otra instancia.
- Reiniciar o escalar el servicio no eliminará conversaciones almacenadas porque el servidor no las conservará.
- Se reduce el tratamiento de datos conversacionales y la complejidad de privacidad, expiración y sincronización.
- La continuidad dependerá de que Banorte reproduzca correctamente el historial relevante en cada solicitud.
- El tamaño máximo de historial aceptado deberá definirse y validarse al confirmar el contrato real.

### Validación

La decisión se comprobará mediante una conversación de varios turnos en la que Banorte envíe la transcripción previa y el agente responda correctamente una pregunta de seguimiento sin consultar almacenamiento de sesiones.

Se deberá verificar también que una solicitud independiente, sin historial, no reciba información procedente de conversaciones anteriores.

### Condición de revisión

La decisión se revisará si una solicitud real demuestra que Banorte no reproduce el historial necesario, si exige `previous_response_id` o si aparece un requisito explícito de continuidad entre dispositivos o sesiones que no pueda resolverse con la transcripción recibida.

## D06. Modalidad de respuesta completa y streaming

**Estado:** Aceptada para el MVP; streaming condicionado a la integración real  
**Fecha:** 2026-08-18

### Contexto

El contrato preliminar contempla respuestas completas en JSON y transmisión incremental mediante Server-Sent Events (SSE). Todavía no existe evidencia de cuál modalidad solicitará realmente la plataforma de Banorte ni de los eventos incrementales que consume su interfaz.

Las respuestas del agente de CV serán normalmente breves, pero algunas explicaciones sobre proyectos, investigaciones o experiencia pueden beneficiarse de mostrar contenido antes de terminar la generación.

### Decisión

Se implementará primero la modalidad de **respuesta completa no streaming**.

- Cuando `stream` sea `false` o no esté presente, el endpoint devolverá una respuesta completa con `Content-Type: application/json`.
- La recuperación RAG y la generación deberán funcionar y estar probadas en esta modalidad antes de incorporar SSE.
- La arquitectura interna conservará interfaces separadas para generación completa y generación incremental, evitando acoplar el RAG a una modalidad de transporte.
- SSE será una capacidad condicional durante el MVP.
- Si una solicitud real de Banorte contiene `stream: true`, el soporte SSE se convertirá en requisito obligatorio antes de la entrega.
- Una solicitud con `stream: true` no deberá tratarse silenciosamente como `stream: false`.
- La modalidad definitiva aceptada se confirmará mediante una prueba desde la plataforma de Banorte.

### Evaluación por criterio

| Criterio | Respuesta completa | Streaming SSE |
|---|---|---|
| Experiencia de usuario | Adecuada para respuestas breves; el contenido aparece al terminar | Mejora la percepción de velocidad en respuestas extensas |
| Contrato | Contemplada en el contrato preliminar mediante `stream: false` o su ausencia | Contemplada mediante `stream: true`, pero su uso real por Banorte no está confirmado |
| Proxies y nube | Compatible con el comportamiento HTTP convencional | Puede sufrir buffering, timeout o cierre anticipado; requiere validación en el despliegue real |
| Complejidad | Una respuesta, un estado final y errores HTTP directos | Requiere eventos ordenados, vaciado incremental, desconexión, errores parciales y cierre correcto |
| Prioridad | Obligatoria y primera en implementarse | Condicional hasta recibir evidencia de uso |

### Requisitos para SSE si se activa

Si Banorte solicita streaming, la implementación deberá:

- Responder con `Content-Type: text/event-stream`.
- Emitir la secuencia de eventos exigida por el subconjunto de Open Responses que consuma Banorte.
- Mantener identificadores y números de secuencia coherentes.
- Propagar texto incremental sin repetir ni perder fragmentos.
- Representar fallos ocurridos después de iniciar la transmisión.
- Detectar la desconexión del cliente y cancelar trabajo innecesario cuando sea posible.
- Cerrar la transmisión conforme al contrato confirmado.
- Superar pruebas a través del proxy y la plataforma de nube seleccionados, no sólo en ejecución local.

### Validación

La modalidad no streaming se considerará validada cuando una solicitud con `stream: false` o sin el campo produzca una respuesta JSON válida que Banorte muestre correctamente.

Antes de cerrar la integración se deberá observar si Banorte envía `stream: true`. Si lo hace, D06 no estará completamente validada hasta que una secuencia SSE sea aceptada y finalizada correctamente desde la plataforma.

### Condición de revisión

La prioridad podrá cambiar si Banorte confirma que siempre solicita streaming, si establece un límite de tiempo incompatible con respuestas completas o si las mediciones muestran que la espera perjudica de forma material la experiencia conversacional.

## D07. Estrategia de autenticación de entrada

**Estado:** Implementada y probada localmente; pendiente de integración con Banorte
**Fecha:** 2026-08-18

### Contexto

El formulario de Banorte indica que la clave configurada para el agente se enviará al endpoint mediante el encabezado `Authorization: Bearer ...`. El endpoint utilizará servicios externos con credenciales propias, por lo que es necesario separar la autenticación de entrada de las claves empleadas para llamar a OpenAI u otros proveedores.

Se evaluaron estas alternativas:

| Alternativa | Ventajas | Limitaciones |
|---|---|---|
| Clave estática mediante Bearer | Coincide con la interfaz observada de Banorte, utiliza un esquema HTTP estándar y es sencilla de probar | Requiere proteger, distribuir y rotar el secreto |
| Clave en encabezado personalizado | Permite definir un nombre propio como `x-api-key` | No existe evidencia de que Banorte permita configurar otro encabezado |
| Endpoint sin autenticación | Elimina la configuración de credenciales | Permite abuso, acceso no autorizado y consumo de cuota; Banorte no lo exige actualmente |

### Decisión

`POST /v1/responses` se protege mediante una **clave estática Bearer independiente**, almacenada como variable de entorno.

- La credencial de entrada se llamará `AGENT_API_KEY`.
- Banorte enviará `Authorization: Bearer <AGENT_API_KEY>`.
- `AGENT_API_KEY` será distinta de `OPENAI_API_KEY` y de cualquier clave de un proveedor de modelos.
- La aplicación no incluirá valores reales de estas claves en código, documentación, pruebas, respuestas ni registros.
- Las solicitudes sin credencial o con una credencial inválida recibirán HTTP `401` y `WWW-Authenticate: Bearer`.
- El cuerpo del error será genérico y no revelará si una clave concreta existe, expiró o coincide parcialmente.
- La comparación de la credencial evitará comparaciones inseguras dependientes del tiempo cuando la implementación lo permita.
- `GET /health` permanecerá público y no devolverá configuración, información profesional, estado del índice ni secretos.
- No se habilitará un endpoint público sin autenticación para generar respuestas, salvo que Banorte lo exija explícitamente.

### Separación de credenciales

| Variable | Autoriza | Se configura en |
|---|---|---|
| `AGENT_API_KEY` | A Banorte para invocar el endpoint del agente | Servicio desplegado y formulario de Banorte |
| `OPENAI_API_KEY` | Al servidor para invocar OpenAI | Únicamente en el servicio desplegado o entorno local |
| Credencial de contingencia | Al servidor para invocar el proveedor alternativo | Únicamente en el servicio desplegado o entorno local |

La clave registrada en el formulario de Banorte nunca deberá ser `OPENAI_API_KEY`.

### Rotación

La clave podrá rotarse sin modificar ni volver a compilar el código:

1. Generar una nueva clave aleatoria.
2. Reemplazar `AGENT_API_KEY` en las variables de entorno del servicio.
3. Reiniciar o desplegar nuevamente la instancia para cargarla, si la plataforma lo requiere.
4. Actualizar la clave del agente en Banorte.
5. Probar una solicitud autorizada y confirmar que la clave anterior ya no funciona.

Si la plataforma no permite actualizar ambos extremos dentro de una ventana suficientemente corta, se podrá añadir temporalmente soporte para una clave actual y una anterior mediante configuración, sin incorporarlas al código.

### Validación

D07 se considerará implementada cuando existan pruebas automatizadas que demuestren:

- Acceso exitoso con una clave válida.
- HTTP `401` sin encabezado de autorización.
- HTTP `401` con esquema o clave inválidos.
- Acceso público a `/health` sin exponer información sensible.
- Sustitución de `AGENT_API_KEY` mediante configuración, sin editar el código.
- Ausencia de secretos reales en Git y en los registros de las pruebas.

La implementación local se encuentra en `app/auth.py` y su evidencia automatizada
en `tests/test_auth.py`. La comparación utiliza `hmac.compare_digest`; las pruebas
usan una credencial ficticia y no leen la clave personal de `.env`.

### Condición de revisión

La estrategia se revisará si Banorte exige un encabezado diferente, un endpoint abierto, claves múltiples, firma de solicitudes, OAuth u otro mecanismo de autenticación no observable en la configuración actual.

## D08. Plataforma de despliegue

**Estado:** Aceptada  
**Fecha:** 2026-08-18  
**Aprobación de costo:** Mario acepta el plan Railway Hobby con cuota base de USD $5 al mes.

### Contexto

El agente necesita una URL HTTPS pública y estable, ejecución de un contenedor FastAPI, configuración segura de secretos, registros operativos, posibilidad de transmitir SSE y disponibilidad durante el periodo de evaluación. El RAG utiliza Chroma embebido, por lo que también resulta conveniente disponer de almacenamiento persistente.

Se compararon Railway, Render y Google Cloud Run:

| Criterio | Railway Hobby | Render gratuito | Google Cloud Run |
|---|---|---|---|
| HTTPS y URL estable | Certificado automático y dominio de Railway | Certificado automático y dominio de Render | Endpoint HTTPS estable |
| Docker | Soporte directo | Soporte directo | Soporte directo |
| Streaming SSE | Soporte directo sobre HTTP; sujeto a límites de duración | Requiere validación a través de su proxy | Soporta respuestas HTTP incrementales |
| Logs | Registros de construcción, despliegue, aplicación y solicitudes | Registros del servicio | Cloud Logging integrado |
| Secretos | Variables administradas por servicio | Variables administradas | Secret Manager o configuración del servicio |
| Persistencia de Chroma | Volumen persistente disponible | El plan gratuito no admite disco persistente | El sistema de archivos de las instancias es efímero |
| Cold start | Evitable manteniendo Serverless desactivado | El servicio gratuito se suspende después de inactividad | Escala a cero de forma predeterminada; se puede configurar una instancia mínima con costo |
| Región considerada | California, Estados Unidos | Oregon, Estados Unidos | México disponible |
| Costo inicial | Hobby: USD $5 al mes con USD $5 de uso incluido; puede generar excedentes | Gratuito con restricciones incompatibles con una evaluación confiable | Pago por uso; mantener instancias activas genera costo |
| Complejidad operativa | Baja | Baja | Media o alta por IAM, secretos y estrategia de persistencia |

### Decisión

La plataforma principal será **Railway**, utilizando el plan **Hobby**.

- El servicio se desplegará como un contenedor Docker.
- La región inicial será **US West, California**.
- Railway Serverless permanecerá desactivado durante la integración y el periodo de evaluación para evitar cold starts.
- El servicio tendrá una URL HTTPS estable proporcionada por Railway.
- La aplicación escuchará en `0.0.0.0` y utilizará el puerto indicado por la variable `PORT`.
- `GET /health` se configurará como comprobación de disponibilidad.
- Se montará un volumen persistente para el índice de Chroma y `CHROMA_PATH` apuntará a dicho volumen.
- `OPENAI_API_KEY`, `AGENT_API_KEY` y cualquier credencial de contingencia se configurarán como variables del servicio, nunca dentro de la imagen ni del repositorio.
- La aplicación escribirá registros estructurados en salida estándar sin claves, encabezados de autorización ni transcripciones completas.
- Si se activa SSE, se comprobará desde el dominio público de Railway y no solamente en local.
- Los despliegues se realizarán desde el repositorio mediante una configuración reproducible.

### Costo y control de consumo

Mario acepta la cuota base de USD $5 mensuales del plan Hobby. Según la documentación de Railway, esa cuota incluye USD $5 de consumo; si el uso supera esa cantidad, se cobra la diferencia.

- Se configurará una alerta de uso antes de la demostración.
- Se revisará el consumo después de las pruebas de carga y durante el periodo de disponibilidad.
- No se asumirá que el costo máximo será exactamente USD $5.
- Cualquier límite estricto deberá configurarse con cuidado, porque alcanzar un límite que apague el servicio afectaría la evaluación.
- No se habilitarán réplicas, servicios adicionales ni recursos de mayor tamaño sin una necesidad medida y aprobación de Mario.

### Estrategia de persistencia

El volumen de Railway conservará el índice Chroma entre reinicios y despliegues. El índice seguirá siendo un artefacto reconstruible desde los seis documentos autorizados:

- Una pérdida del volumen no deberá implicar pérdida de la fuente de conocimiento.
- La aplicación deberá detectar un índice ausente o incompatible y reconstruirlo mediante un proceso controlado.
- El volumen no almacenará conversaciones ni credenciales.
- La ubicación exacta del montaje se definirá en la configuración del despliegue y se reflejará mediante `CHROMA_PATH`.

### Alternativa de contingencia

Google Cloud Run en `northamerica-south1` será la alternativa si Railway presenta una incompatibilidad comprobada, indisponibilidad o un bloqueo de cuenta que impida completar la entrega.

Utilizar Cloud Run requeriría resolver explícitamente la persistencia o reconstrucción del índice, la gestión mediante Secret Manager y la política de instancias mínimas.

Render gratuito no se utilizará para la entrega porque su suspensión por inactividad y ausencia de disco persistente introducen riesgos de disponibilidad y latencia. Un plan pagado podría reconsiderarse únicamente como alternativa adicional.

### Validación

D08 se considerará implementada cuando exista evidencia de que:

- El contenedor se construye y arranca correctamente en Railway.
- La URL pública utiliza HTTPS y permanece estable entre despliegues.
- `/health` responde desde una red externa.
- `/responses` funciona con autenticación desde la URL pública.
- Las variables secretas pueden rotarse sin cambiar el código.
- El índice Chroma permanece disponible después de reiniciar el servicio o puede reconstruirse de manera controlada.
- Los logs permiten diagnosticar solicitudes sin divulgar secretos ni transcripciones completas.
- Una prueba SSE funciona a través del proxy público si Banorte activa `stream: true`.
- El servicio permanece activo sin cold start durante el periodo de evaluación.
- El consumo y costo observados quedan registrados.

### Condición de revisión

La decisión se revisará si Railway no puede ejecutar las dependencias dentro de los recursos seleccionados, no conserva el volumen, interfiere con el contrato de Banorte, excede el presupuesto aceptado o presenta fallas de disponibilidad durante las pruebas.

### Referencias

- [Railway: planes y precios](https://docs.railway.com/pricing/plans)
- [Railway: red pública y HTTPS](https://docs.railway.com/networking/public-networking)
- [Railway: límites de red](https://docs.railway.com/networking/public-networking/specs-and-limits)
- [Railway: volúmenes](https://docs.railway.com/volumes/reference)
- [Railway: regiones](https://docs.railway.com/deployments/regions)
- [Railway: modo Serverless](https://docs.railway.com/deployments/serverless)
- [Railway: logs](https://docs.railway.com/observability/logs)
- [Google Cloud Run: solicitudes HTTPS y streaming](https://docs.cloud.google.com/run/docs/triggering/https-request)
- [Google Cloud Run: sistema de archivos efímero](https://docs.cloud.google.com/run/docs/overview/what-is-cloud-run)

## DC01. Identidad, interfaz y alcance conversacional

**Estado:** Aceptada  
**Fecha:** 2026-08-18  
**Fuente:** Instrucciones y formulario de Banorte; decisión directa de Mario.

### Contexto

La plataforma de Banorte proporciona el chat, permite seleccionar el agente y consume su endpoint público. No existe una regla confirmada que obligue a hablar en primera o tercera persona. La solución debe representar la trayectoria de Mario sin confundir al usuario ni afirmar que el software es una persona humana.

### Decisión

- No se construirá una interfaz gráfica propia para el MVP; Banorte será el cliente conversacional.
- El agente se presentará explícitamente como **el agente profesional de Mario**.
- Utilizará primera persona por defecto al describir la trayectoria de Mario para mantener una conversación natural.
- No afirmará ser una persona humana ni inventará opiniones, emociones, intereses o experiencias.
- Limitará sus respuestas al perfil profesional autorizado.
- Ante información ausente, privada o no verificable, reconocerá la limitación y no completará la respuesta mediante suposiciones.

### Consecuencias

- El prompt de sistema deberá aplicar esta identidad y conservarla frente a instrucciones contradictorias del usuario.
- Las pruebas deberán incluir primera interacción, preguntas de seguimiento, cambios de persona, información desconocida, solicitudes confidenciales e intentos de inyección.
- Swagger, pruebas automatizadas o clientes HTTP podrán utilizarse durante el desarrollo, pero no formarán parte de la experiencia final del usuario.

## DC02. Estrategia interna de evaluación y entrega

**Estado:** Aceptada  
**Fecha:** 2026-08-18  
**Fuente:** Decisión directa de Mario; no constituye una rúbrica oficial de Banorte.

### Contexto

No se dispone de una rúbrica oficial con porcentajes. El reto sí enfatiza que la solución debe funcionar y demostrar criterio para construir, integrar, desplegar y operar un producto de IA. Mario considera prioritario explicar por qué se eligió cada componente y qué alternativas fueron descartadas.

### Decisión

- Se utilizarán como condiciones mínimas el funcionamiento extremo a extremo, respuestas claras y fundamentadas, ausencia de divulgaciones críticas, despliegue reproducible y publicación segura del repositorio.
- La evaluación interna asignará 30 % a calidad y RAG, 30 % a arquitectura y decisiones, 20 % a despliegue y operación, 10 % a seguridad y privacidad, y 10 % a documentación y presentación.
- Estas ponderaciones se presentarán siempre como criterios internos, nunca como calificación o ponderación atribuida a Banorte.
- El repositorio final será público e incluirá README, decisiones, arquitectura y evidencia de evaluación.
- La presentación formará parte de la entrega; el video o la demostración en vivo se prepararán posteriormente.
- El endpoint permanecerá disponible durante al menos 15 días después de la entrega y Mario lo retirará manualmente al concluir ese periodo.
- No se incorporarán tecnologías únicamente para aparentar complejidad. Cada componente deberá resolver una necesidad identificable y tener una justificación verificable.

### Evidencia y revisión

Los criterios completos están en `docs/criterios-evaluacion.md`. La ponderación podrá ajustarse antes de la evaluación final si Banorte publica una rúbrica oficial; cualquier cambio deberá conservar el historial y distinguir la fuente de cada criterio.
