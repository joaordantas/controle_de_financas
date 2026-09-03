# Controle de Financas

Projeto pessoal em evolucao para controle financeiro, vendas e cobrancas.

## Estado atual
- App legado em Streamlit continua disponivel em `app.py`
- Nova API em FastAPI criada em `backend/`
- Novo frontend React + TypeScript criado em `frontend/`
- Banco SQLite continua em `storage/banco.db`

## Objetivo da migracao
Migrar gradualmente do Streamlit para uma interface propria em React, mantendo o backend em Python e transformando a logica atual em uma API reutilizavel.

## Estrutura principal
```text
backend/      -> nova API FastAPI
frontend/     -> nova interface React + TypeScript
database/     -> conexao e schema SQLite
repositories/ -> acesso a dados
services/     -> regras de negocio
storage/      -> banco SQLite
app.py        -> app legado em Streamlit
```

## O que ja foi iniciado
- Rotas de autenticacao
- Rotas de categorias
- Rotas de transacoes
- Rotas de dashboard
- Rotas de vendas e parcelas
- Estrutura visual inicial em React
- Refatoracao inicial dos services
- Fluxo atomico para pagamento de parcela + lancamento financeiro

## Como rodar o backend
1. Crie e ative um ambiente virtual
2. Instale dependencias:
```bash
pip install -r requirements.txt
```
3. Rode a API:
```bash
uvicorn backend.main:app --reload
```

## Como rodar o frontend
Requisito: ter Node.js e npm instalados.

1. Entre na pasta do frontend:
```bash
cd frontend
```
2. Instale dependencias:
```bash
npm install
```
3. Rode o projeto:
```bash
npm run dev
```

Frontend padrao:
- URL: `http://localhost:5173`
- API esperada: `http://127.0.0.1:8000`

Se quiser trocar a URL da API depois, crie um `.env` no `frontend/` com:
```bash
VITE_API_URL=http://127.0.0.1:8000
```

## Como rodar o app antigo
```bash
streamlit run app.py
```

## Proximos passos sugeridos
- Testar a API rota por rota
- Instalar Node.js para validar o frontend
- Migrar o login real na nova interface
- Migrar categorias e financeiro por fluxo completo
- Revisar o app Streamlit para consumir services mais claros quando fizer sentido

## Guias de estudo
- `docs/trilha-estudos.md`
- `docs/anotacoes-projeto.md`
- `docs/comandos-uteis.md`
