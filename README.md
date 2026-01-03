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
```
conda create -n backend-cliro python=3.12
conda activate backend-cliro
bash```
2. Instalar dependencias desde requirements.txt
```
pip install -r requirements.txt
bash```
3. Ejecutar servidor (backend)
```
uvicorn app.main:app --reload
bash```

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

```
    from fastapi import FastAPI
    from app.routers import auth, ai

    app = FastAPI(title="AI Extension Backend")

    app.include_router(auth.router, prefix="/auth")
    app.include_router(ai.router, prefix="/ai")
bash```

---

📁 app/core/
Contiene configuración y seguridad transversal al sistema.

**app/core/**
core/config.py
Variables de entorno y configuración global.
```
SUPABASE_URL = os.getenv("SUPABASE_URL")
bash```

**core/security.py**
Tokens y validación de acceso.
```
def verify_token(token: str): ...
bash```
---

📁 app/routers/
**routers/auth.py**
Rutas de waitlist y login simple.
- POST /auth/waitlist
- POST /auth/login

```
@router.post("/waitlist")
def join_waitlist(data): ...
bash```

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

```
email: str
language: str
...
bash```

**schemas/ai.py**
Input de acciones de IA.
```
text: str
action: str
bash```
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
```
supabase = create_client(...)
bash```

---

📁 app/utils/
**utils/crypto.py**
Helpers de cifrado y hashing.
```
def hash_value(value): ...
bash```

---

📁 tests/
Tests unitarios y de integración.
```
test_auth.py
test_ai.py
...
bash```