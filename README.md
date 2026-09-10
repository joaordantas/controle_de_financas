# Controle de Finanças

Assistente financeiro pessoal construído com FastAPI, React, TypeScript e SQLite. O produto busca reduzir o trabalho manual necessário para registrar, acompanhar e entender as finanças pessoais.

## Fase atual

**Fase 2 — Núcleo Financeiro concluída.**

A Fase 1 estabeleceu a nova fundação do frontend, com rotas reais, layout responsivo, navegação para desktop e celular e componentes visuais reutilizáveis.

A Fase 2 entrega:

- contas financeiras e saldo por conta;
- receitas e despesas vinculadas a contas;
- transferências que não alteram receitas ou despesas;
- histórico unificado de receitas, despesas e transferências;
- busca e filtros por tipo, conta, categoria e período;
- edição e exclusão de movimentações com recálculo de saldos;
- edição, ativação e desativação segura de contas;
- criação de categorias dentro do registro de movimentações;
- proteção contra categorias duplicadas ou em uso;
- Dashboard conectado ao saldo das contas;
- tema claro e escuro com identidade visual em índigo.

O próximo passo planejado é a **Fase 3 — Planejamento Financeiro**, com cartões, faturas, parcelamentos, recorrências, orçamentos e metas. Ela ainda não foi iniciada.

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

O frontend fica disponível em `http://localhost:5173` e usa `http://127.0.0.1:8000/api` como API por padrão. A variável abaixo deve informar somente a origem, pois o prefixo `/api` é acrescentado pela aplicação.

Para configurar outra URL, crie `frontend/.env`:

```bash
VITE_API_URL=http://127.0.0.1:8000
```

## Publicar uma versão de demonstração na Vercel

O repositório possui configuração para a Vercel localizar o FastAPI, compilar o frontend Vite e servir ambos pelo mesmo domínio. Ao conectar a branch `main`, mantenha o diretório raiz do projeto como Root Directory e deixe a detecção automática cuidar do build.

Na Vercel, o SQLite usa armazenamento temporário e pode ser reiniciado entre execuções. Essa configuração serve apenas para demonstração. Antes de usar o produto com dados reais em produção, o banco deverá ser migrado para PostgreSQL ou outro armazenamento persistente.

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
