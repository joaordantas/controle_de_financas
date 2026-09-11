# Relatório da Fase 3A — Conta principal, cartões e faturas

Data de conclusão: 11 de setembro de 2026.

## Situação das fases

- Fase 1 — concluída.
- Fase 2 — concluída.
- Fase 3A — concluída.
- Fase 3B — pendente.
- Fase 3C — pendente.
- Fase 3D — pendente.
- Fase 3E — pendente.

Esta entrega ficou restrita à conta principal, cartões, compras no cartão, ciclos, faturas, limite e pagamento integral. Parcelamentos, recorrências, orçamentos, metas, IA, notificações e integrações externas não foram iniciados.

## O que foi implementado

### Conta principal

Cada usuário pode escolher no máximo uma conta ativa como principal. A troca remove a marcação anterior e define a nova dentro de uma transação `BEGIN IMMEDIATE`, evitando estados intermediários ou duas contas principais.

As regras aplicadas são:

- a conta precisa pertencer ao usuário informado;
- uma conta inativa não pode ser principal;
- ao trocar a principal, a anterior perde a marcação;
- ao desativar a principal, sua marcação é removida;
- nenhuma outra conta é escolhida automaticamente após a desativação;
- transações e transferências antigas não são alteradas.

A conta principal aparece primeiro na listagem e recebe uma identificação visual. Ela é usada como seleção inicial para receitas, despesas, origem de transferências e pagamento de faturas. O usuário continua podendo escolher outra conta.

### Conta mais utilizada

O uso é calculado sob demanda, sem armazenar uma classificação permanente. A consulta considera os últimos 90 dias e soma:

- receitas e despesas vinculadas à conta;
- origem e destino de transferências;
- pagamentos de fatura realizados pela conta.

A API retorna `percentual_uso` e `mais_utilizada`. A página de Contas mostra a participação nas movimentações recentes. Em caso de empate, as contas empatadas podem aparecer como mais utilizadas; nenhuma delas é definida automaticamente como principal.

### Cartões de crédito

O cartão pertence a um usuário e contém nome, limite total, dia de fechamento, dia de vencimento, situação e datas de criação/atualização.

As validações impedem:

- limite igual ou inferior a zero;
- dias fora do intervalo de 1 a 31;
- redução do limite para um valor inferior ao já utilizado;
- consulta ou alteração usando outro usuário;
- novas compras em cartão inativo;
- nomes duplicados para o mesmo usuário.

Desativar um cartão preserva cartões, faturas, compras e pagamentos anteriores. A reativação permite novas compras novamente.

### Compras no cartão

Uma compra exige cartão ativo, categoria pertencente ao mesmo usuário, valor positivo, descrição e data válida. Ela não reduz imediatamente nenhuma conta financeira.

Ao criar ou editar uma compra, o service calcula o ciclo correspondente e vincula a compra à fatura correta. Edições podem mudar cartão, data, categoria, valor e descrição enquanto a fatura não estiver paga. Exclusões também são permitidas somente antes do pagamento. Ao editar ou excluir, total da fatura e limite são recalculados a partir das compras existentes.

### Regra do ciclo de fatura

A regra fica centralizada em `calcular_ciclo_fatura()` no service de cartões.

Para um cartão que fecha no dia 13 e vence no dia 20:

- compra em 12/09 entra na fatura com fechamento em 13/09;
- compra em 13/09 também entra nessa fatura;
- compra em 14/09 entra na fatura seguinte, com fechamento em 13/10.

Quando o vencimento é posterior ao fechamento, ele permanece no mesmo mês do fechamento. Quando o dia de vencimento é igual ou anterior ao dia de fechamento, o vencimento fica no mês seguinte. Dias que não existem no mês são limitados ao último dia válido. A regra cobre fevereiro, anos bissextos e dezembro para janeiro.

Cada fatura armazena o intervalo, fechamento e vencimento calculados no momento de sua criação. Assim, uma alteração futura nos dias do cartão não muda ciclos históricos.

### Estados da fatura

O estado não é armazenado como texto fixo. Ele é derivado no service a partir das datas, do total e do pagamento:

- `aberta`: a data atual ainda não passou do fechamento;
- `fechada`: o fechamento passou, o vencimento ainda não passou e não houve pagamento;
- `vencida`: o vencimento passou e não houve pagamento;
- `paga`: existe pagamento integral suficiente para o total da fatura.

O estado pago tem prioridade sobre as datas. Uma fatura aberta pode ser paga antecipadamente.

### Limite

O banco armazena somente o limite total. Os demais valores são derivados:

- limite utilizado: soma das compras pertencentes a faturas ainda não pagas;
- limite disponível: limite total menos limite utilizado;
- percentual utilizado: limite utilizado dividido pelo limite total.

Compras pagas deixam de comprometer o limite. Essa consulta poderá ser ampliada na Fase 3B para considerar a entidade de parcelamento e seu comprometimento futuro.

### Regra contábil e dupla contagem

A regra adotada é:

- compra no cartão representa a despesa econômica;
- pagamento da fatura representa a liquidação da obrigação;
- o pagamento reduz o saldo da conta escolhida;
- o pagamento não cria outra receita ou despesa.

Os resumos gerais e por período somam compras no cartão às saídas. O saldo de cada conta deduz pagamentos de fatura. Como o pagamento não entra novamente no resumo de despesas, uma compra de R$ 100 continua representando R$ 100 de gasto depois que a fatura é paga.

### Pagamento da fatura

Esta versão aceita somente pagamento integral. A operação valida fatura, usuário, conta ativa e ausência de pagamento anterior. O registro ocorre dentro de uma transação imediata e a restrição única em `fatura_id` reforça a proteção contra pagamento duplicado.

O pagamento fica em tabela própria. Isso separa a obrigação da liquidação e permite evoluir para pagamentos parciais futuramente, quando a regra de negócio estiver definida. Para suportá-los, será necessário remover a unicidade por fatura e calcular o total pago pela soma dos lançamentos.

## Modelagem do banco

### Alteração em `contas`

- `principal INTEGER NOT NULL DEFAULT 0`.
- índice único parcial por `usuario_id` quando `principal = 1` e `ativo = 1`.

### Nova tabela `cartoes`

Armazena proprietário, nome, limite total, dias de fechamento e vencimento, situação e timestamps. Nome é único por usuário.

### Nova tabela `faturas`

Armazena cartão, proprietário, ano/mês de referência, início do ciclo, fechamento, vencimento e criação. Existe uma fatura por cartão e período de referência.

### Nova tabela `compras_cartao`

Armazena cartão, fatura, proprietário, categoria, valor, descrição, data e timestamps. O vínculo com a fatura é decidido pelo service.

### Nova tabela `pagamentos_fatura`

Armazena fatura, conta financeira, proprietário, valor, data e criação. A fatura é única nesta tabela porque a Fase 3A suporta pagamento integral único.

Valores derivados, como total da fatura, estado, limite utilizado e limite disponível, não foram duplicados em colunas.

## Endpoints

- `PATCH /api/accounts/{conta_id}/primary`
- `GET /api/cards`
- `POST /api/cards`
- `PUT /api/cards/{cartao_id}`
- `PATCH /api/cards/{cartao_id}/status`
- `GET /api/cards/{cartao_id}/invoices`
- `GET /api/cards/{cartao_id}/invoices/current`
- `GET /api/invoices/{fatura_id}`
- `POST /api/card-purchases`
- `PUT /api/card-purchases/{compra_id}`
- `DELETE /api/card-purchases/{compra_id}`
- `POST /api/invoices/{fatura_id}/pay`

Todos mantêm o prefixo `/api` e a separação router, schema, service, repository e banco.

## Frontend

A rota `/cards` passou a usar uma página funcional. Ela permite:

- listar cartões ativos e inativos;
- criar, editar, desativar e reativar cartão;
- ver fatura atual, limite disponível e percentual utilizado;
- cadastrar uma compra com os campos essenciais;
- abrir histórico e detalhes de uma fatura;
- editar e excluir compras não pagas;
- pagar integralmente usando uma conta ativa;
- selecionar a conta principal como padrão para o pagamento;
- informar estados de carregamento, ausência de dados, sucesso e erro.

Os formulários de cartão e compra foram separados em componentes reutilizáveis. O layout foi validado em desktop e em viewport de 390 × 844 pixels, com navegação mobile ativa e sem rolagem horizontal.

O Dashboard não recebeu um novo bloco nesta fase. Os valores de gastos já incorporam compras no cartão pelo resumo existente, evitando adicionar informação visual antes do trabalho específico de inteligência financeira.

## Arquivos criados

- `backend/routers/cards.py`
- `backend/schemas/cards.py`
- `repositories/cartao_repo.py`
- `services/cartao_service.py`
- `frontend/src/components/finance/CardForm.tsx`
- `frontend/src/components/finance/CardPurchaseForm.tsx`
- `frontend/src/pages/CardsPage.tsx`
- `tests/test_phase3a.py`
- `docs/relatorio-fase-3a.md`

## Arquivos alterados

- `README.md`
- `backend/main.py`
- `backend/routers/accounts.py`
- `backend/schemas/accounts.py`
- `database/schema.py`
- `repositories/conta_repo.py`
- `repositories/categoria_repo.py`
- `repositories/dashboard_repo.py`
- `repositories/transacao_repo.py`
- `services/conta_service.py`
- `frontend/src/app/router.tsx`
- `frontend/src/components/finance/MovementForm.tsx`
- `frontend/src/components/ui/Feedback.tsx`
- `frontend/src/pages/AccountsPage.tsx`
- `frontend/src/pages/TransactionsPage.tsx`
- `frontend/src/services/api.ts`
- `frontend/src/styles.css`
- `frontend/src/types.ts`

## Testes automatizados

Foram adicionados 13 testes específicos da Fase 3A. Junto aos 6 testes de regressão da Fase 2, a suíte possui 19 testes.

As regras verificadas incluem:

- primeira definição e troca atômica da conta principal;
- unicidade, conta inativa, outro usuário e remoção ao desativar;
- funcionamento sem conta principal;
- criação, edição, ativação, desativação e isolamento de cartão;
- compras antes, no dia e depois do fechamento;
- fevereiro e virada de dezembro para janeiro;
- estados derivados da fatura;
- validação de categoria, cartão ativo e limite;
- edição, mudança de ciclo e exclusão de compra;
- total da fatura e limites disponível/utilizado;
- pagamento, saldo da conta e liberação do limite;
- bloqueio de pagamento duplicado e uso de conta de outro usuário;
- preservação e imutabilidade de fatura paga;
- ausência de dupla contagem no resumo financeiro.

Resultado final: 19 testes executados e 19 aprovados.

## Outras verificações

- compilação Python de `backend`, `database`, `repositories` e `services`: aprovada;
- consistência das dependências Python com `pip check`: aprovada;
- TypeScript e build de produção Vite: aprovados;
- pacote principal do frontend: 324,41 kB, 98,51 kB compactado;
- OpenAPI: 10 caminhos principais da Fase 3A validados;
- health check, documentação da API e fallback da SPA: HTTP 200;
- teste visual de Contas e CardsPage: aprovado;
- teste responsivo em 390 × 844: aprovado e sem overflow horizontal.

## Problemas encontrados e corrigidos

- o nome da coluna de atualização da compra divergia do schema; foi alinhado com `atualizada_em`;
- a nova coluna da conta alterou a posição do saldo no resultado SQL; o índice usado pelo service foi corrigido;
- origem e destino de uma transferência podiam iniciar com a mesma conta; agora sempre começam diferentes;
- depois de trocar a principal, a origem da transferência mantinha a seleção anterior até recarregar; agora atualiza imediatamente;
- abrir a edição de compra sobre os detalhes da fatura criava modais sobrepostos; o detalhe é fechado antes da edição;
- respostas de validação em lista apareciam como `[object Object]`; o cliente agora extrai mensagens legíveis;
- índices de leitura de fatura precisaram ser atualizados após incluir `data_inicio`; os testes de ciclo e pagamento cobrem a correção.

## Limitações e riscos conhecidos

- a autenticação ainda usa o mecanismo temporário existente. Os services conferem o mesmo `usuario_id` em todas as relações, mas uma identidade autenticada no backend é necessária para impedir que alguém forje outro ID em produção;
- SQLite continua sendo adequado para desenvolvimento e demonstração. O uso de `BEGIN IMMEDIATE`, índice parcial e `INSERT OR IGNORE` precisará de adaptação ao migrar para PostgreSQL;
- pagamentos parciais não são aceitos;
- uma fatura pode ser paga antes do fechamento;
- compras de faturas fechadas ou vencidas podem ser corrigidas enquanto não houver pagamento;
- o cartão mostra o ciclo atual mesmo quando ele já foi pago; o estado aparece no histórico e nos detalhes;
- o cálculo de conta mais utilizada trata origem e destino de transferência como usos separados e pode produzir empate;
- não há parcelamento ou comprometimento futuro nesta entrega.

## Considerações antes da Fase 3B

A modelagem de parcelamento deverá criar uma entidade principal da compra parcelada e gerar parcelas relacionadas aos ciclos futuros. Antes de implementar, é preciso definir:

- como o valor total compromete o limite desde a compra;
- regras de arredondamento entre parcelas;
- edição ou cancelamento após algumas parcelas pagas;
- antecipação de parcelas;
- diferença entre exclusão da compra e estorno;
- apresentação de parcelas atuais e futuras sem duplicar a despesa econômica;
- migração do cálculo de limite para considerar saldos de parcelas ainda não liquidadas.

A Fase 3B não foi iniciada.
