# Roadmap público da Nivra

Este roadmap organiza a evolução da Nivra por capacidades do produto. As datas e versões podem mudar conforme validações técnicas e de uso.

## Foundation

- [x] React e TypeScript
- [x] FastAPI
- [x] Rotas e navegação
- [x] Interface responsiva
- [x] Tema claro e escuro
- [x] Componentes reutilizáveis

## Core Finance

- [x] Dashboard financeiro
- [x] Contas e saldos
- [x] Conta principal
- [x] Receitas
- [x] Despesas
- [x] Transferências neutras em receitas e despesas
- [x] Categorias
- [x] Histórico unificado
- [x] Busca e filtros
- [x] Criação, edição e exclusão

## Infrastructure

- [x] PostgreSQL como banco oficial
- [x] Neon como provider atual
- [x] Persistência remota
- [x] SQLAlchemy Core
- [x] Alembic migrations
- [x] Configuração serverless para Vercel
- [x] Importador seguro do SQLite legado
- [ ] Autenticação segura para produção
- [ ] Sessão no backend com cookie HTTP-only

## Cards and Invoices

- [x] Cartões
- [x] Limite total, utilizado e disponível
- [x] Ciclos de fatura
- [x] Fatura atual e histórico
- [x] Compras no cartão
- [x] Pagamento integral por conta financeira
- [ ] Pagamentos parciais
- [ ] Estornos e ajustes avançados

## Financial Planning

- [ ] Parcelamentos pessoais e projeções futuras
- [ ] Transações recorrentes
- [ ] Orçamentos por categoria
- [ ] Alertas de orçamento
- [ ] Metas financeiras
- [ ] Projeções de comprometimento

## Intelligence

- [ ] Comparação entre períodos
- [ ] Motor determinístico de insights
- [ ] Detecção de gastos incomuns
- [ ] Área “Sua atenção” baseada em regras
- [ ] Lumi — assistente financeira inteligente
- [ ] Consultas em linguagem natural
- [ ] Ações financeiras com confirmação

## Automation

- [ ] Centro de notificações
- [ ] Eventos financeiros
- [ ] Alertas configuráveis
- [ ] Resumo semanal
- [ ] Resumo mensal
- [ ] Notificações por WhatsApp

## Professional Mode — futuro

- [ ] Clientes
- [ ] Vendas e serviços
- [ ] Recebimentos
- [ ] Estoque
- [ ] Lucro e margens
- [ ] Indicadores comerciais

## Direção de versionamento

| Linha | Objetivo aproximado |
| --- | --- |
| `v0.1.x-alpha` | Core financeiro e infraestrutura persistente |
| `v0.2.x-alpha` | Maturidade de cartões, faturas e parcelamentos |
| `v0.3.x-alpha` | Planejamento financeiro, orçamentos e metas |
| `v0.4.x-beta` | Insights e maturidade financeira |
| `v0.5.x-beta` | Lumi e linguagem natural |
| `v0.6.x-beta` | Notificações e automação |
| `v1.0.0` | Primeira versão pública considerada estável |

Essa sequência é uma direção de produto. Uma versão só será promovida quando suas capacidades e limitações estiverem documentadas e validadas.
