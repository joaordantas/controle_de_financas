# Relatório — Autenticação segura

Data da atualização: 11 de setembro de 2026.

## Resultado

A Nivra deixou de usar o `usuario_id` enviado pelo React como identidade. Todas as APIs privadas agora identificam o usuário por uma sessão criada e validada pelo FastAPI. A sessão é persistida no PostgreSQL e enviada ao navegador por cookie HTTP-only.

O trabalho ficou limitado à autenticação, autorização e proteção das APIs atuais. Nenhuma funcionalidade de parcelamento, recorrência, orçamento, meta, Open Finance, Lumi ou notificação foi iniciada.

## Modelo anterior

Antes desta atualização:

- o usuário retornado pelo login era salvo no `localStorage`;
- o frontend enviava `usuario_id` em consultas, bodies e URLs;
- um cliente poderia tentar trocar esse identificador manualmente;
- logout removia somente o estado local;
- não existia sessão revogável no backend;
- operações de escrita não possuíam proteção CSRF.

Os services já verificavam a propriedade das entidades, mas recebiam a identidade escolhida pelo cliente. Essa era a principal limitação para testes externos com múltiplos usuários.

## Arquitetura final

```text
React
  │ cookie HTTP-only + token CSRF
  ▼
FastAPI
  │ current_user
  ▼
Routers
  ▼
Services com validação de propriedade
  ▼
Repositories
  ▼
PostgreSQL / Neon
```

O React nunca recebe o token da sessão. Ele recebe somente os dados públicos do usuário autenticado pelo endpoint `/api/auth/me`.

## Sessões no PostgreSQL

A migration `7a4c9d2e1f30` adiciona a tabela `sessoes`:

| Campo | Responsabilidade |
| --- | --- |
| `id` | identificador interno |
| `usuario_id` | usuário proprietário, com exclusão em cascata |
| `token_hash` | hash SHA-256 do token aleatório, único |
| `csrf_hash` | hash do token CSRF vinculado à sessão |
| `criada_em` | data de criação |
| `expira_em` | limite de validade |
| `revogada_em` | revogação explícita pelo logout ou expiração |

O valor bruto do cookie de sessão não é persistido. Se o banco for consultado, somente o hash está disponível.

Foram criados índices para o usuário e a expiração. A restrição única do token e a chave primária também possuem índices gerenciados pelo PostgreSQL.

## Cookies e expiração

- nome da sessão: `nivra_session`;
- `HttpOnly`: ativo;
- `SameSite`: `Lax`;
- `Secure`: ativo quando `APP_ENV=production` ou `VERCEL_ENV=production`;
- `Path`: `/`;
- validade padrão: 168 horas, configurável com `SESSION_TTL_HOURS` entre 1 e 8760 horas.

Uma sessão expirada é rejeitada e marcada como revogada. O logout revoga a sessão no PostgreSQL e remove os cookies do navegador.

## Proteção CSRF

O endpoint `GET /api/auth/csrf` entrega um token de dupla submissão. Operações `POST`, `PUT`, `PATCH` e `DELETE` enviam esse valor em `X-CSRF-Token`; o backend compara header, cookie e hash vinculado à sessão.

Login e cadastro também exigem o token. Para uma sessão válida, o endpoint reutiliza o token atual, evitando que duas abas abertas invalidem uma à outra.

## Contrato das APIs

Foram adicionados:

- `GET /api/auth/csrf`;
- `GET /api/auth/me`;
- `POST /api/auth/logout`.

O campo ou parâmetro `usuario_id` foi removido dos contratos protegidos de:

- contas e transferências;
- categorias;
- transações e resumo;
- dashboard;
- cartões, compras e faturas;
- vendas e parcelas existentes no backend.

As rotas de leitura usam `CurrentUser`. Rotas que alteram dados usam `CurrentUserCsrf`. Os schemas de entrada rejeitam campos extras, portanto um `usuario_id` inserido artificialmente no body retorna erro de validação.

## Frontend

O cliente HTTP passou a:

- usar `credentials: include`;
- obter CSRF automaticamente antes da primeira alteração;
- não aceitar nem enviar `usuario_id`;
- restaurar a identidade por `/api/auth/me` ao abrir o site;
- tratar `401` como encerramento de sessão;
- revogar a sessão no backend ao sair.

O antigo registro `controle-financas-user` é removido durante a inicialização. O `localStorage` continua sendo usado somente para preferência visual de tema.

As rotas aguardam a verificação inicial da sessão antes de decidir entre login e área protegida, evitando redirecionamento incorreto durante o carregamento.

## CORS

As origens locais aceitas são exatamente:

- `http://localhost:5173`;
- `http://127.0.0.1:5173`.

Origens adicionais precisam ser declaradas em `CORS_ORIGINS`, separadas por vírgula. A configuração não usa mais expressão ampla para portas arbitrárias. Métodos e headers permitidos foram limitados ao conjunto usado pela aplicação.

No deploy integrado da Nivra, React e FastAPI compartilham `https://nivra-finance.vercel.app`, portanto não dependem de CORS para a comunicação normal.

## Neon e migration

A migration foi aplicada no branch principal do projeto `nivra-db` pelo editor SQL do Neon, dentro de uma transação. Nenhuma tabela financeira ou registro existente foi alterado.

Validações após a execução:

- `alembic_version`: `7a4c9d2e1f30`;
- tabela `sessoes`: criada com 7 colunas;
- índices identificados: 4, incluindo chave primária, token único e os dois índices explícitos;
- migration anterior confirmada antes da alteração: `13ecd0272470`.

O arquivo versionado do Alembic continua sendo a fonte oficial para novos ambientes:

```bash
alembic upgrade head
```

## GitHub e produção

O código principal da atualização foi registrado no commit `42b4e8b` (`feat(auth): concluir autenticação segura v0.2`) e enviado para a branch `main` do repositório Nivra.

Após o deploy automático da Vercel, a aplicação pública foi validada em `https://nivra-finance.vercel.app`:

- página de login carregada;
- `/api/health`: `200`, com banco online;
- `/openapi.json`: `200`;
- `/api/auth/me` sem cookie: `401`, como esperado;
- `/api/auth/me` e `/api/auth/csrf` presentes no OpenAPI;
- `usuario_id` ausente do contrato público.

O teste de login com um usuário real permanece uma verificação manual do proprietário, pois nenhuma credencial foi lida, solicitada ou criada durante esta atualização.

## Testes de segurança

A nova suíte cobre:

- bloqueio de rota privada sem sessão;
- CSRF obrigatório em login e cadastro;
- cookie HTTP-only e SameSite;
- atributo Secure em produção e na Vercel;
- persistência da sessão entre clientes;
- armazenamento exclusivo do hash do token;
- restauração por `/api/auth/me`;
- CSRF vinculado à sessão;
- uso em múltiplas abas;
- logout com revogação no banco;
- rejeição e revogação de sessão expirada;
- tentativa de falsificar `usuario_id`;
- isolamento real entre dois usuários;
- CORS restrito;
- ausência de `usuario_id` no OpenAPI.

As regras financeiras existentes continuam testadas em conjunto para garantir que a mudança de identidade não alterou saldos, transferências, cartões ou faturas.

Resultados finais:

- 44 testes automatizados aprovados;
- build React e TypeScript aprovado;
- compilação dos módulos Python aprovada;
- Alembic em `head` e `alembic check` sem operações pendentes;
- FastAPI iniciado localmente com sucesso;
- `/api/health`, OpenAPI e `/api/auth/csrf` responderam `200`;
- uma rota financeira sem sessão respondeu `401`, como esperado;
- links relativos da documentação validados;
- nenhum segredo real identificado nos arquivos alterados.

## Arquivos criados

- `backend/dependencies/__init__.py`;
- `backend/dependencies/auth.py`;
- `repositories/sessao_repo.py`;
- `services/session_service.py`;
- `migrations/versions/7a4c9d2e1f30_secure_sessions.py`;
- `tests/auth_support.py`;
- `tests/test_secure_auth.py`;
- `docs/relatorio-autenticacao-segura.md`.

## Grupos de arquivos alterados

- conexão pública e CORS: `backend/main.py`, `.env.example`;
- routers e schemas protegidos em `backend/routers/` e `backend/schemas/`;
- metadata do banco em `database/models.py`;
- importador legado em `scripts/migrate_sqlite_to_postgres.py` para reconhecer a nova revisão;
- cliente HTTP, provider de autenticação, rotas e páginas React em `frontend/src/`;
- testes de API e dashboard;
- `README.md`, `CHANGELOG.md`, arquitetura, desenvolvimento e roadmap.

## Compatibilidade e limites conhecidos

- sessões antigas não existiam e, portanto, todos os usuários precisarão entrar novamente após o deploy;
- recuperação e alteração de senha ainda não existem;
- não há histórico de dispositivos nem ação de encerrar todas as sessões;
- rate limiting de login continua planejado;
- verificação de e-mail ainda não foi definida;
- a Nivra continua em Alpha e ainda precisa de monitoramento, auditoria, políticas públicas e outros itens de preparação para produção.

## Próxima etapa

Conforme o roadmap aprovado, a próxima etapa funcional é **Parcelamentos e recorrências**. Ela não faz parte desta atualização e deve começar somente após revisão deste relatório.
