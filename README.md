# Controle de Finanças

Assistente financeiro pessoal com frontend React/TypeScript, API FastAPI e PostgreSQL. A aplicação é hospedada na Vercel e usa atualmente o Neon como provedor de banco persistente.

## Estado do projeto

As Fases 1 e 2 entregaram a fundação visual responsiva e o núcleo de finanças pessoais: autenticação inicial, contas, saldos, receitas, despesas, transferências, categorias, histórico, busca e filtros. A Fase 3A já existente permanece preservada, mas está pausada enquanto a infraestrutura PostgreSQL é estabilizada.

O SQLite em `storage/banco.db` é somente uma cópia legada para importação. Ele não é mais aberto pelo backend e nunca deve ser usado como persistência na Vercel.

## Arquitetura

```text
React na Vercel
       ↓ /api
FastAPI na Vercel
       ↓
Services → Repositories → SQLAlchemy → PostgreSQL/Neon
```

O frontend não recebe credenciais do banco. O backend mantém a divisão entre routers, schemas, services, repositories e database.

## Variáveis de ambiente

Use `.env.example` como referência e defina as variáveis no terminal, na IDE ou no provedor de hospedagem:

```env
APP_ENV=development
DATABASE_URL=postgresql://usuario:senha@ep-exemplo-pooler.regiao.aws.neon.tech/neondb?sslmode=require
DATABASE_URL_UNPOOLED=postgresql://usuario:senha@ep-exemplo.regiao.aws.neon.tech/neondb?sslmode=require
```

- `DATABASE_URL`: conexão com pooling usada pela aplicação. No Neon, prefira o host com `-pooler` para o ambiente serverless.
- `DATABASE_URL_UNPOOLED`: conexão direta usada por Alembic e pelo importador. É recomendada, mas o sistema usa `DATABASE_URL` se ela não existir.
- `APP_ENV`: use `development` localmente e `production` na Vercel.
- `TEST_DATABASE_URL`: banco exclusivo dos testes. A suíte recusa reutilizar `DATABASE_URL`.

Nenhuma dessas variáveis pode começar com `VITE_`, pois isso a exporia no bundle do navegador.

## Instalação e desenvolvimento

Use Python 3.12, instale as dependências e configure as variáveis antes de iniciar a API:

```bash
python -m venv .venv
pip install -r requirements.txt
alembic upgrade head
uvicorn backend.main:app --reload
```

A documentação da API fica em `http://127.0.0.1:8000/docs`. O endpoint `/api/health` também verifica a conexão com o banco.

Para executar o frontend:

```bash
cd frontend
npm ci
npm run dev
```

O frontend usa `http://127.0.0.1:8000/api` no desenvolvimento. Para trocar a origem da API, defina apenas uma URL pública em `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Migrations

O schema é controlado pelo Alembic. A API não cria nem altera tabelas durante o startup.

```bash
alembic upgrade head
alembic current
alembic revision --autogenerate -m "descricao da alteracao"
```

Execute migrations de produção de forma controlada com `DATABASE_URL_UNPOOLED`. Não coloque `alembic upgrade head` no startup da função serverless.

## Migrar o SQLite antigo

O importador preserva IDs e relacionamentos, grava tudo em uma única transação e nunca apaga o arquivo original.

Primeiro analise a origem, sem escrever no PostgreSQL:

```bash
python scripts/migrate_sqlite_to_postgres.py
```

Para autorizar exclusivamente os três registros órfãos já auditados a ficarem fora do PostgreSQL:

```bash
python scripts/migrate_sqlite_to_postgres.py --skip-known-orphans
```

O comando continua sendo um dry-run. Ele confere o conteúdo completo dos três registros e bloqueia qualquer órfão novo. Depois de revisar o relatório e aplicar as migrations no PostgreSQL, execute a importação uma única vez:

```bash
python scripts/migrate_sqlite_to_postgres.py --execute --skip-known-orphans
```

Por segurança, o importador recusa um destino que já contenha dados. Para retomar uma importação conhecida, `--allow-existing` ignora apenas IDs já presentes e mantém as demais constraints ativas:

```bash
python scripts/migrate_sqlite_to_postgres.py --execute --skip-known-orphans --allow-existing
```

O dry-run atual identifica três registros financeiros órfãos no banco legado: duas transações pertencentes a usuários removidos (`usuario_id` 1 e 2) e uma venda ligada ao usuário removido 1. A opção explícita mantém esses registros somente no SQLite original. O arquivo não é alterado.

## Testes

```bash
python -m unittest discover -s tests -v
cd frontend
npm run build
```

Os testes definem `APP_ENV=test`, usam um SQLite descartável criado pelas migrations e jamais selecionam `DATABASE_URL` automaticamente. Para uma suíte futura contra PostgreSQL, configure um `TEST_DATABASE_URL` separado e descartável; nunca use o projeto de produção do Neon.

## Configuração na Vercel

Mantenha o diretório raiz do repositório como Root Directory. Nas configurações do projeto, cadastre para Production, Preview e Development conforme necessário:

```text
APP_ENV=production
DATABASE_URL=<URL pooled do Neon>
DATABASE_URL_UNPOOLED=<URL direta do Neon>
```

Antes do primeiro deploy, rode `alembic upgrade head` usando a URL direta. Depois, importe o SQLite uma única vez se os dados legados forem necessários. A configuração exclui `storage/**` da função, portanto a produção não depende de arquivos locais.

## Verificação de persistência

1. Crie um usuário de teste no site publicado.
2. Crie uma conta, uma categoria, uma receita, uma despesa e uma transferência.
3. Confirme os saldos e o histórico.
4. Faça um novo deploy sem alterar o banco Neon.
5. Entre novamente e confirme que todos os registros permanecem.
6. Crie um segundo usuário e confirme que as listas de contas, categorias e movimentações não exibem dados do primeiro.

A autenticação atual ainda guarda a identificação do usuário no `localStorage` e envia `usuario_id` à API. Os services validam a propriedade dos dados, mas sessão segura com cookie HTTP-only continua como etapa obrigatória antes do uso com dados sensíveis.

## Guias do projeto

- `docs/trilha-estudos.md`
- `docs/anotacoes-projeto.md`
- `docs/comandos-uteis.md`
- `docs/relatorio-fases-1-e-2.md`
- `docs/relatorio-fase-3a.md`
- `docs/relatorio-migracao-postgresql.md`
