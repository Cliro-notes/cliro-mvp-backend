# Backend de Cliro Notes para el MVP (simple y sencillo)
Aqui se debe creat un backend en FastAPI. Algo parecido a esto (consultar con ChatGPT):

backend/

├─ app/

│  ├─ main.py

│  │
│  ├─ core/
│  │  ├─ config.py        # env vars
│  │  └─ security.py      # encryption, tokens
│  │
│  ├─ routers/
│  │  ├─ auth.py          # waitlist signup / login
│  │  └─ ai.py            # all AI actions
│  │
│  ├─ schemas/
│  │  ├─ auth.py          # waitlist input
│  │  └─ ai.py            # AI request/response
│  │
│  ├─ services/
│  │  ├─ auth_service.py
│  │  └─ ai_service.py
│  │
│  ├─ db.py               # Supabase / DB access
│  │
│  └─ utils/
│     └─ crypto.py        # encryption helpers
│
├─ tests/
└─ requirements.txt
