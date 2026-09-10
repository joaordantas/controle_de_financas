import { ArrowDownLeft, ArrowRight, ArrowUpRight, CheckCircle2, CircleDollarSign, Plus, ReceiptText } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../app/providers";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { Feedback } from "../components/ui/Feedback";
import { PageHeader } from "../components/ui/PageHeader";
import { api } from "../services/api";
import type { Account, ProfitSummary, Transaction } from "../types";
import { formatCurrency, formatDate, getCurrentMonthRange } from "../utils/formatters";

export function DashboardPage() {
  const { user } = useAuth();
  const period = useMemo(getCurrentMonthRange, []);
  const [profit, setProfit] = useState<ProfitSummary>({ entrada: 0, saida: 0, lucro: 0 });
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    const userId = user.id;

    async function loadDashboard() {
      try {
        setLoading(true);
        const [profitData, transactionData, accountData] = await Promise.all([
          api.getProfit(userId, period.start, period.end),
          api.getTransactions(userId),
          api.getAccounts(userId),
        ]);
        setProfit(profitData);
        setTransactions(transactionData.slice(0, 5));
        setAccounts(accountData);
        setError("");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Não foi possível carregar seu resumo financeiro.");
      } finally {
        setLoading(false);
      }
    }

    void loadDashboard();
  }, [period.end, period.start, user]);

  const firstName = user?.usuario.split(" ")[0] ?? "";
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Bom dia" : hour < 18 ? "Boa tarde" : "Boa noite";
  const totalBalance = accounts.reduce((total, account) => total + account.saldo_atual, 0);
  const attentionTitle = transactions.length === 0
    ? "Tudo pronto para começar"
    : profit.lucro >= 0
      ? "Seu mês está positivo"
      : "Seus gastos passaram das entradas";
  const attentionDescription = transactions.length === 0
    ? "Registre uma movimentação para começar a acompanhar seu mês."
    : profit.lucro >= 0
      ? `Você mantém ${formatCurrency(profit.lucro)} depois dos gastos registrados.`
      : `A diferença atual é de ${formatCurrency(Math.abs(profit.lucro))}.`;

  return (
    <div className="page-stack">
      <PageHeader
        action={<Link className="button button-primary" to="/transactions?new=1#new-transaction"><Plus size={18} />Nova transação</Link>}
        description="Veja o que importa nas suas finanças agora."
        eyebrow={period.label}
        title={`${greeting}, ${firstName}`}
      />

      {error ? <Feedback>{error}</Feedback> : null}

      <Card className="balance-card">
        <div>
          <span className="card-label">Saldo registrado</span>
          {loading ? <span className="skeleton skeleton-value" /> : <strong>{formatCurrency(accounts.length ? totalBalance : profit.lucro)}</strong>}
          <small>{accounts.length ? `Somado entre ${accounts.length} ${accounts.length === 1 ? "conta" : "contas"}` : "Adicione suas contas para acompanhar o patrimônio disponível"}</small>
        </div>
        <span className="balance-icon"><CircleDollarSign aria-hidden="true" size={26} /></span>
      </Card>

      <section aria-label="Resumo do mês" className="summary-grid">
        <Card className="summary-card">
          <span className="summary-icon income"><ArrowDownLeft size={18} /></span>
          <span>Entradas</span>
          {loading ? <span className="skeleton skeleton-line" /> : <strong>{formatCurrency(profit.entrada)}</strong>}
        </Card>
        <Card className="summary-card">
          <span className="summary-icon expense"><ArrowUpRight size={18} /></span>
          <span>Gastos</span>
          {loading ? <span className="skeleton skeleton-line" /> : <strong>{formatCurrency(profit.saida)}</strong>}
        </Card>
        <Card className="summary-card">
          <span className="summary-icon savings"><CircleDollarSign size={18} /></span>
          <span>Economizado</span>
          {loading ? <span className="skeleton skeleton-line" /> : <strong>{formatCurrency(Math.max(profit.lucro, 0))}</strong>}
        </Card>
      </section>

      <div className="dashboard-grid">
        <Card className="attention-card">
          <div className="card-heading">
            <div>
              <span className="section-kicker">Sua atenção</span>
              <h2>O que merece atenção</h2>
            </div>
          </div>
          <div className="attention-item attention-positive">
            <span><CheckCircle2 aria-hidden="true" size={20} /></span>
            <div>
              <strong>{attentionTitle}</strong>
              <p>{attentionDescription}</p>
            </div>
          </div>
          <p className="attention-note">Novos alertas aparecerão aqui conforme orçamentos, contas e cartões forem adicionados.</p>
        </Card>

        <Card className="recent-card">
          <div className="card-heading card-heading-row">
            <div>
              <span className="section-kicker">Movimentações</span>
              <h2>Transações recentes</h2>
            </div>
            <Link className="text-link" to="/transactions">Ver todas <ArrowRight size={16} /></Link>
          </div>

          {loading ? (
            <div className="transaction-list" aria-label="Carregando transações">
              {[1, 2, 3].map((item) => <span className="skeleton skeleton-row" key={item} />)}
            </div>
          ) : transactions.length === 0 ? (
            <EmptyState
              action={<Link className="button button-secondary" to="/transactions?new=1#new-transaction">Adicionar transação</Link>}
              description="Adicione sua primeira movimentação para começar a acompanhar suas finanças."
              icon={ReceiptText}
              title="Nenhuma transação ainda"
            />
          ) : (
            <div className="transaction-list">
              {transactions.map((transaction) => {
                const isIncome = transaction.tipo === "entrada";
                return (
                  <div className="transaction-row" key={transaction.id}>
                    <span className={`transaction-icon ${isIncome ? "income" : "expense"}`}>
                      {isIncome ? <ArrowDownLeft size={18} /> : <ArrowUpRight size={18} />}
                    </span>
                    <span className="transaction-info">
                      <strong>{transaction.comentario || transaction.categoria || (isIncome ? "Receita" : "Despesa")}</strong>
                      <small>{transaction.categoria || "Sem categoria"} · {transaction.conta} · {formatDate(transaction.data)}</small>
                    </span>
                    <strong className={isIncome ? "amount-income" : "amount-expense"}>
                      {isIncome ? "+" : "−"} {formatCurrency(transaction.valor)}
                    </strong>
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
