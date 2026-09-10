# Comandos Uteis

## Backend
Instalar dependencias:
```bash
pip install -r requirements.txt
```

Rodar API:
```bash
uvicorn backend.main:app --reload
```

## Frontend
Entrar na pasta:
```bash
cd frontend
```

Instalar dependencias:
```bash
npm install
```

Rodar frontend:
```bash
npm run dev
```

## Dicas
- Rode backend e frontend em terminais separados
- Se a API nao abrir, teste `http://127.0.0.1:8000/docs`
- Se o frontend nao abrir, confirme se Node.js e npm estao instalados
