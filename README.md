# Controle de Finanças

Assistente financeiro pessoal construído com FastAPI, React, TypeScript e SQLite. O produto busca reduzir o trabalho manual necessário para registrar, acompanhar e entender as finanças pessoais.

## Fase atual

**Fase 2 — Núcleo Financeiro em andamento.**

A Fase 1 estabeleceu a nova fundação do frontend, com rotas reais, layout responsivo, navegação para desktop e celular e componentes visuais reutilizáveis.

O primeiro bloco da Fase 2 adiciona:

- contas financeiras e saldo por conta;
- receitas e despesas vinculadas a contas;
- transferências que não alteram receitas ou despesas;
- busca e filtro básico de transações;
- Dashboard conectado ao saldo das contas;
- tema claro e escuro com identidade visual em índigo.

Ainda fazem parte da Fase 2: edição e desativação de contas, edição e exclusão de transações, filtros por período e melhorias na gestão de categorias.

## Estrutura principal

```text
backend/      API FastAPI e rotas
database/     conexão e criação incremental do schema SQLite
repositories/ persistência de dados
services/     regras de negócio
frontend/     interface React + TypeScript
storage/      banco SQLite de desenvolvimento
tests/        testes automatizados do núcleo financeiro
```

## Executar o backend

Crie e ative um ambiente virtual, instale as dependências e inicie a API:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

A documentação da API fica disponível em `http://127.0.0.1:8000/docs`.

## Executar o frontend

Com Node.js e npm instalados:

```bash
cd frontend
npm install
npm run dev
```

O frontend fica disponível em `http://localhost:5173` e usa `http://127.0.0.1:8000` como API por padrão.

Para configurar outra URL, crie `frontend/.env`:

```bash
VITE_API_URL=http://127.0.0.1:8000
```

## Verificações

```bash
python -m unittest discover -s tests -v
cd frontend
npm run build
```

## Guias do projeto

- `docs/trilha-estudos.md`
- `docs/anotacoes-projeto.md`
- `docs/comandos-uteis.md`
