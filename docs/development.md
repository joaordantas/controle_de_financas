# Desenvolvimento da Nivra

## Requisitos

- Python 3.12;
- Node.js e npm;
- PostgreSQL acessível;
- Git.

## Backend

Crie o ambiente virtual e instale as dependências:

```bash
python -m venv .venv
pip install -r requirements.txt
```

Defina as variáveis descritas em `.env.example` no seu terminal ou na configuração da IDE. Use valores próprios e nunca versione credenciais.

```text
APP_ENV=development
DATABASE_URL=<conexao PostgreSQL da aplicacao>
DATABASE_URL_UNPOOLED=<conexao direta para migrations>
```

Aplique o schema e inicie a API:

```bash
alembic upgrade head
uvicorn backend.main:app --reload
```

Endereços locais:

- API: `http://127.0.0.1:8000/api`;
- health check: `http://127.0.0.1:8000/api/health`;
- OpenAPI: `http://127.0.0.1:8000/docs`.

## Frontend

```bash
cd frontend
npm ci
npm run dev
```

O Vite inicia normalmente em `http://127.0.0.1:5173`. Quando necessário, `VITE_API_URL` deve conter somente a origem pública da API.

## Testes

```bash
python -m unittest discover -s tests -v
cd frontend
npm run build
```

A suíte usa `APP_ENV=test` e um banco descartável definido em `TEST_DATABASE_URL`. As proteções impedem que `DATABASE_URL` de produção seja selecionada automaticamente para testes.

## Migrations

```bash
alembic current
alembic upgrade head
alembic revision --autogenerate -m "descricao da alteracao"
alembic check
```

Revise toda migration gerada antes de aplicá-la. Não execute downgrade ou reset contra um banco com dados reais.

## SQLite legado

O arquivo `storage/banco.db` não é o banco oficial. O importador lê esse arquivo sem modificá-lo e exige opções explícitas para gravar ou ignorar os três registros órfãos auditados.

Dry-run:

```bash
python scripts/migrate_sqlite_to_postgres.py --skip-known-orphans
```

Importação deliberada:

```bash
python scripts/migrate_sqlite_to_postgres.py --execute --skip-known-orphans
```

Consulte [o relatório da migração](relatorio-migracao-postgresql.md) antes de executar a importação.

## Deploy na Vercel

Configure no ambiente desejado:

- `APP_ENV`;
- `DATABASE_URL`;
- `DATABASE_URL_UNPOOLED`.

O build integrado instala as dependências do frontend, gera o bundle Vite e publica o FastAPI pelo entrypoint `backend.main:app`. A migration deve ser aplicada de forma controlada antes do primeiro acesso ao banco de um ambiente novo.

## Renomeação dos serviços externos

A troca do nome público no GitHub e na Vercel é uma operação manual e separada do código. Consulte o [guia de renomeação externa](renomeacao-externa.md) antes de alterar qualquer serviço. O projeto Neon já usa o nome `nivra-db` e não precisa ser modificado.

## Convenções

- regras financeiras ficam em services;
- persistência fica em repositories;
- routers não recebem regras de negócio;
- credenciais nunca ficam no frontend;
- funcionalidades futuras não devem ser apresentadas como disponíveis;
- mudanças de schema exigem migration.
