# AgenteCV — Conversational CV Agent (Reto IA Banorte)

Agente conversacional de CV desarrollado con FastAPI, RAG ligero (OpenAI Embeddings + ChromaDB) y protocolo Open Responses para responder preguntas verificables sobre experiencia, formación, habilidades, proyectos y publicaciones profesionales de Mario Alberto Román Garay.

Banorte proporciona la interfaz de chat que consume el endpoint desplegado; este repositorio contiene la API backend, el motor RAG, la base de conocimiento curada y la suite de evaluación y pruebas.

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

### 2. Configurar clave de OpenAI

Edita el archivo `.env` local (este archivo **nunca** debe subirse a Git):

```text
OPENAI_API_KEY=tu_clave_privada
```

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
