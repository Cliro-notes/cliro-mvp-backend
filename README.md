# Backend de Cliro Notes para el MVP (simple y sencillo)
Aqui se debe creat un backend en FastAPI que se conecte con Supabase. Para enviar en formato JSON data al frontend

Este backend está diseñado para soportar un **MVP / MLP** enfocado en:

- Registro de usuarios en **waitlist** (sin passwords, auth ligera)
- Rutas protegidas para **acciones de IA** usadas para la extensión
- Escalabilidad futura (billing, ML, analytics, etc.)
- Uso de **Supabase como DB**
- Seguridad mediante **tokens y cifrado**

La arquitectura sigue principios de:
- Separación de responsabilidades
- Bajo acoplamiento
- Escalabilidad progresiva

Estructura Resumida:
- routers → HTTP
- services → lógica
- schemas → contratos
- core → seguridad/config
- utils → helpers

---
## Ejecucion

1. Crear y activar el entorno Conda
```bash
conda create -n backend-cliro python=3.12
conda activate backend-cliro
```
2. Instalar dependencias desde requirements.txt
```bash
pip install -r requirements.txt
```
3. Ejecutar servidor (backend)
```bash
uvicorn app.main:app --reload
```

---

## Estructura / Arquitectura

```txt
backend/
├─ app/
│  ├─ main.py
│  │
│  ├─ core/
│  │  ├─ config.py
│  │  └─ security.py
│  │
│  ├─ routers/
│  │  ├─ auth.py
│  │  └─ ai.py
│  │
│  ├─ schemas/
│  │  ├─ auth.py
│  │  └─ ai.py
│  │
│  ├─ services/
│  │  ├─ auth_service.py
│  │  └─ ai_service.py
│  │
│  ├─ db.py
│  │
│  └─ utils/
│     └─ crypto.py
│
├─ tests/
└─ requirements.txt
```

📌 app/main.py
Punto de entrada del backend
Responsabilidades:

- Crear la instancia de FastAPI
- Registrar routers
- Configurar middlewares globales (CORS, logging, etc.)

```bash
    from fastapi import FastAPI
    from app.routers import auth, ai

    app = FastAPI(title="AI Extension Backend")

    app.include_router(auth.router, prefix="/auth")
    app.include_router(ai.router, prefix="/ai")
```

---

📁 app/core/
Contiene configuración y seguridad transversal al sistema.

**app/core/**
core/config.py
Variables de entorno y configuración global.
```bash
SUPABASE_URL = os.getenv("SUPABASE_URL")
```

**core/security.py**
Tokens y validación de acceso.
```bash
def verify_token(token: str): ...
```
---

📁 app/routers/
**routers/auth.py**
Rutas de waitlist y login simple.
- POST /auth/waitlist
- POST /auth/login

```bash
@router.post("/waitlist")
def join_waitlist(data): ...
```

**routers/ai.py**
Rutas de acciones de IA (protegidas).
- POST /ai/summarize
- POST /ai/translate
- POST /ai/rewrite
...

---

📁 app/schemas/
Define contratos de datos (request / response).

**schemas/auth.py**
Input de waitlist.

```bash
email: str
language: str
...
```

**schemas/ai.py**
Input de acciones de IA.
```bash
text: str
action: str
```
---

📁 app/services/
Lógica de negocio (sin HTTP).

**services/auth_service.py**
- Guardar waitlist
- Generar tokens
- Validar usuarios

**services/ai_service.py**
- Construir prompts
- Llamar APIs de IA
- Registrar eventos

---

📌 app/db.py
Conexión centralizada a Supabase.
```bash
supabase = create_client(...)
```

---

📁 app/utils/
**utils/crypto.py**
Helpers de cifrado y hashing.
```bash
def hash_value(value): ...
```

---

📁 tests/
Tests unitarios y de integración.
```bash
test_auth.py
test_ai.py
...
```