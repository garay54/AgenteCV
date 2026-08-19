# AgenteCV — Conversational CV Agent (Reto IA Banorte)

Agente conversacional de CV desarrollado con FastAPI, RAG ligero (OpenAI Embeddings + ChromaDB) y protocolo Open Responses para responder preguntas verificables sobre experiencia, formación, habilidades, proyectos y publicaciones profesionales de Mario Alberto Román Garay.

Banorte proporciona la interfaz de chat que consume el endpoint desplegado; este repositorio contiene la API backend, el motor RAG, la base de conocimiento curada y la suite de evaluación y pruebas.

## Estado actual

- API base desplegada en Railway con HTTPS, healthcheck y autenticación Bearer; el despliegue público debe actualizarse con el incremento de generación real.
- RAG local construido con 55 fragmentos curados y evaluación real aprobada.
- Suite automatizada: 39 pruebas aprobadas.
- `POST /v1/responses` conecta localmente recuperación RAG, prompt fundamentado y `gpt-5.6-luna` mediante Responses API.
- Flujo real local validado con HTTP 200, modelo efectivo y uso de tokens reportado; falta desplegar este incremento y validarlo desde Banorte.

### Resultado de recuperación

La evaluación reproducible más reciente ejecutó 49 consultas single-turn con `text-embedding-3-small`, Chroma y reranking híbrido ligero:

| Métrica | Resultado |
|---|---:|
| Hit@3 | 100 % |
| Hit@4 | 100 % |
| Top-1 | 81.63 % |
| MRR@4 | 90.48 % |
| Errores | 0 |
| Documentos excluidos recuperados | 0 |

Reporte: `artifacts/evaluations/retrieval-20260818-221152.json`. Estas cifras evalúan recuperación; la generación y las conversaciones multitur­no requieren una evaluación posterior.

---

## Corpus autorizado para producción

El índice RAG incorpora exclusivamente los siguientes documentos curados:

- `knowledge/profile.md`: Perfil profesional, grado académico y fortalezas.
- `knowledge/experience.md`: Experiencia de investigación de posgrado y actividades académicas.
- `knowledge/projects.md`: Proyectos principales (`PJT-01`, `PJT-02`, `PJT-03`).
- `knowledge/skills.md`: Matriz de habilidades con niveles de evidencia.
- `knowledge/publications.md`: Publicaciones científicas en revistas arbitradas.
- `knowledge/research.md`: Síntesis de la Tesis Doctoral y Tesis de Maestría.

*Nota de privacidad y seguridad:* Quedan completamente excluidos del índice RAG documentos originales, fuentes privadas con datos de contacto, `faq.md`, `open_questions.md` y `question_bank.md` (este último utilizado exclusivamente para benchmarking interno).

---

## Estructura del repositorio

```text
AgenteCV/
├── app/                    # Código fuente FastAPI y módulo RAG
│   ├── config.py           # Configuración mediante variables de entorno
│   ├── main.py             # Instancia FastAPI y endpoints
│   └── rag/                # Chunking, embeddings, vector store y servicio RAG
├── knowledge/              # Base de conocimiento curada en Markdown
├── scripts/                # Scripts de automatización (build_index, evaluate_retrieval)
├── tests/                  # Suite de pruebas unitarias e integración con PyTest
├── docs/                   # Arquitectura, decisiones, contrato API y requisitos
├── .env.example            # Plantilla de configuración de variables de entorno
├── .gitignore              # Reglas de exclusión para Git
├── requirements.txt        # Dependencias de producción
└── requirements-dev.txt    # Dependencias de desarrollo y pruebas
```

---

## Instrucciones de instalación y ejecución local

### 1. Entorno virtual e instalación

Se recomienda Python 3.12 o 3.13.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

### 2. Configurar credenciales locales

Edita el archivo `.env` local (este archivo **nunca** debe subirse a Git):

```text
AGENT_API_KEY=tu_clave_independiente_para_el_agente
OPENAI_API_KEY=tu_clave_privada
OPENAI_GENERATION_MODEL=gpt-5.6-luna
OPENAI_REASONING_EFFORT=none
OPENAI_TEXT_VERBOSITY=low
```

`AGENT_API_KEY` protege `POST /v1/responses` y es la clave que se registrará
en Banorte. Nunca debe reutilizarse como `OPENAI_API_KEY`.

El modelo recibido en el cuerpo de una solicitud no sustituye el modelo configurado
por el servidor. Esto evita que un cliente seleccione modelos no autorizados o más
costosos. Para el MVP, el modelo efectivo es `gpt-5.6-luna`.

### 3. Construir el índice RAG y evaluar recuperación

```powershell
python -m scripts.build_index
python -m scripts.evaluate_retrieval
```

### 4. Ejecutar la API y la suite de pruebas

```powershell
python -m uvicorn app.main:app --reload
python -m pytest
```

- Endpoint de salud: `http://127.0.0.1:8000/health`
- Documentación Swagger: `http://127.0.0.1:8000/docs`

---

## Documentación del proyecto

- `docs/arquitectura.md`: Diseño de la arquitectura RAG y flujo de datos.
- `docs/decisiones.md`: Registro de decisiones técnicas (ADR).
- `docs/criterios-evaluacion.md`: Rúbrica de evaluación interna y calidad.
- `docs/contrato-open-responses.md`: Especificación del contrato de integración con Banorte.
