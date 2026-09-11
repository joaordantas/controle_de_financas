# Arquitetura da Nivra

## Visão geral

```text
                 Nivra
                   │
          React + TypeScript
                   │
                REST /api
                   │
                FastAPI
                   │
                Services
                   │
              Repositories
                   │
           SQLAlchemy Core
                   │
          PostgreSQL / Neon
```

O frontend não acessa o PostgreSQL diretamente. Toda leitura ou alteração passa pela API e pelas regras de negócio do backend.

## Responsabilidades

### Frontend

O diretório `frontend/` contém a interface React, navegação, formulários, feedbacks e temas. O acesso HTTP está centralizado em `frontend/src/services/api.ts`.

### Routers

`backend/routers/` define os endpoints sob `/api`, recebe schemas validados e converte resultados ou erros para respostas HTTP. Routers devem permanecer pequenos.

### Schemas

`backend/schemas/` define contratos de entrada e saída com Pydantic. Essa camada impede que formatos inválidos avancem para as regras financeiras.

### Services

`services/` concentra validações, propriedade dos dados e regras financeiras. Transferências, por exemplo, permanecem neutras no resumo de receitas e despesas.

### Repositories

`repositories/` executa consultas, inserts, updates e deletes. As consultas sempre recebem o contexto do usuário quando a entidade é privada.

### Database

`database/` centraliza engine, conexões, tipos e metadata. PostgreSQL é o banco oficial; Alembic mantém o schema versionado em `migrations/`.

## Persistência e serverless

O backend usa a conexão PostgreSQL fornecida por `DATABASE_URL`. Em Vercel, a aplicação usa a URL pooled do Neon e mantém um pool local pequeno por instância aquecida. Migrations e importações podem usar `DATABASE_URL_UNPOOLED`.

A API não cria tabelas no startup e não depende de arquivos locais para persistência. O SQLite permanece apenas como origem legada e banco descartável de testes.

## Atomicidade

Operações críticas utilizam transações. A troca de conta principal serializa alterações concorrentes, pagamentos de fatura bloqueiam a linha correspondente e uma transferência é persistida como um único evento entre contas.

## Segurança atual

Os services verificam se contas, categorias, transações, transferências e cartões pertencem ao `usuario_id` informado. A autenticação ainda é temporária e deve evoluir para identidade validada no backend antes da versão estável.

## Evolução planejada

As próximas capacidades devem reutilizar services e repositories existentes. Lumi consumirá funções financeiras bem definidas; não terá acesso SQL direto. Notificações serão baseadas em eventos financeiros e canais desacoplados.
