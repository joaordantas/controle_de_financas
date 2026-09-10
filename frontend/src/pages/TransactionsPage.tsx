import { ArrowDownLeft, ArrowUpRight, ReceiptText, Search } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { FormEvent } from "react";
import { useSearchParams } from "react-router-dom";

import { api } from "../services/api";
import { useAuth } from "../app/providers";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { Feedback } from "../components/ui/Feedback";
import { PageHeader } from "../components/ui/PageHeader";
import type { Account, Category, Transaction, TransactionSummary } from "../types";
import { formatCurrency, formatDate } from "../utils/formatters";

export function TransactionsPage() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const formRef = useRef<HTMLElement>(null);
  const today = new Date().toISOString().slice(0, 10);
  const [summary, setSummary] = useState<TransactionSummary>({ entradas: 0, saidas: 0, saldo: 0 });
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [valor, setValor] = useState(0);
  const [tipo, setTipo] = useState<"entrada" | "saida">("saida");
  const [categoriaId, setCategoriaId] = useState<number | null>(null);
  const [accountId, setAccountId] = useState<number | null>(null);
  const [comentario, setComentario] = useState("");
  const [data, setData] = useState(today);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<"todos" | "entrada" | "saida">("todos");

  const filteredTransactions = useMemo(() => {
    const normalizedSearch = search.trim().toLocaleLowerCase("pt-BR");
    return transactions.filter((transaction) => {
      const matchesType = typeFilter === "todos" || transaction.tipo === typeFilter;
      const matchesSearch = !normalizedSearch || [
        transaction.comentario,
        transaction.categoria,
        transaction.conta,
      ].some((value) => value?.toLocaleLowerCase("pt-BR").includes(normalizedSearch));
      return matchesType && matchesSearch;
    });
  }, [search, transactions, typeFilter]);

  async function load() {
    if (!user) return;
    try {
      setLoading(true);
      const [summaryData, transactionData, categoryData, accountData] = await Promise.all([
        api.getTransactionSummary(user.id),
        api.getTransactions(user.id),
        api.getCategories(user.id),
        api.getAccounts(user.id),
      ]);
      setSummary(summaryData);
      setTransactions(transactionData);
      setCategories(categoryData);
      setAccounts(accountData);
      setAccountId((current) => current ?? accountData[0]?.id ?? null);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível carregar suas transações.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [user?.id]);

  useEffect(() => {
    if (searchParams.get("new") === "1") {
      window.requestAnimationFrame(() => formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }));
    }
  }, [searchParams]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!user) return;

    try {
      setSaving(true);
      await api.createTransaction({
        usuario_id: user.id,
        valor,
        tipo,
        categoria_id: tipo === "saida" ? categoriaId : null,
        comentario,
        data,
        conta_id: accountId,
      });
      setValor(0);
      setComentario("");
      setCategoriaId(null);
      setMessage("Transação adicionada com sucesso.");
      setError("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível salvar a transação.");
      setMessage("");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page-stack">
      <PageHeader description="Registre e acompanhe todas as suas movimentações." eyebrow="Organização financeira" title="Transações" />

      {error ? <Feedback>{error}</Feedback> : null}
      {message ? <Feedback tone="success">{message}</Feedback> : null}

      <section className="summary-grid compact-summary" aria-label="Resumo financeiro">
        <Card className="summary-card"><span>Saldo</span><strong>{formatCurrency(summary.saldo)}</strong></Card>
        <Card className="summary-card"><span>Entradas</span><strong className="amount-income">{formatCurrency(summary.entradas)}</strong></Card>
        <Card className="summary-card"><span>Gastos</span><strong>{formatCurrency(summary.saidas)}</strong></Card>
      </section>

      <div className="transactions-layout">
        <section id="new-transaction" ref={formRef}>
        <Card className="transaction-form-card">
          <div className="card-heading">
            <span className="section-kicker">Registro rápido</span>
            <h2>Nova transação</h2>
          </div>

          <form className="form-grid" onSubmit={handleSubmit}>
            <div className="segmented-control" aria-label="Tipo de transação">
              <button className={tipo === "saida" ? "is-active" : ""} onClick={() => setTipo("saida")} type="button"><ArrowUpRight size={17} />Despesa</button>
              <button className={tipo === "entrada" ? "is-active" : ""} onClick={() => setTipo("entrada")} type="button"><ArrowDownLeft size={17} />Receita</button>
            </div>

            <label className="amount-field">
              <span>Valor</span>
              <div><span>R$</span><input min="0.01" onChange={(event) => setValor(Number(event.target.value))} step="0.01" type="number" value={valor || ""} /></div>
            </label>

            <label>
              Descrição
              <input onChange={(event) => setComentario(event.target.value)} placeholder="Ex.: Mercado, salário, academia" value={comentario} />
            </label>

            {tipo === "saida" ? (
              <label>
                Categoria
                <select onChange={(event) => setCategoriaId(event.target.value ? Number(event.target.value) : null)} value={categoriaId ?? ""}>
                  <option value="">Selecione uma categoria</option>
                  {categories.map((category) => <option key={category.id} value={category.id}>{category.nome}</option>)}
                </select>
              </label>
            ) : null}

            <label>
              Conta
              <select onChange={(event) => setAccountId(event.target.value ? Number(event.target.value) : null)} value={accountId ?? ""}>
                <option value="">Sem conta</option>
                {accounts.map((account) => <option key={account.id} value={account.id}>{account.nome}</option>)}
              </select>
            </label>

            <label>
              Data
              <input onChange={(event) => setData(event.target.value)} type="date" value={data} />
            </label>

            <Button disabled={saving || valor <= 0} type="submit">{saving ? "Adicionando..." : "Adicionar transação"}</Button>
          </form>
        </Card>
        </section>

        <Card as="section" className="transactions-history">
          <div className="card-heading card-heading-row">
            <div><span className="section-kicker">Histórico</span><h2>Suas movimentações</h2></div>
            <span className="count-badge">{filteredTransactions.length}</span>
          </div>

          <div className="transaction-filters">
            <label className="search-field"><Search aria-hidden="true" size={17} /><input aria-label="Buscar transações" onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por descrição, categoria ou conta" value={search} /></label>
            <select aria-label="Filtrar por tipo" onChange={(event) => setTypeFilter(event.target.value as typeof typeFilter)} value={typeFilter}>
              <option value="todos">Todos os tipos</option>
              <option value="saida">Despesas</option>
              <option value="entrada">Receitas</option>
            </select>
          </div>

          {loading ? (
            <div className="transaction-list">{[1, 2, 3, 4].map((item) => <span className="skeleton skeleton-row" key={item} />)}</div>
          ) : filteredTransactions.length === 0 ? (
            <EmptyState description={transactions.length === 0 ? "Sua primeira movimentação aparecerá aqui assim que for adicionada." : "Tente ajustar a busca ou o tipo selecionado."} icon={ReceiptText} title={transactions.length === 0 ? "Nenhuma transação registrada" : "Nenhum resultado encontrado"} />
          ) : (
            <div className="transaction-list">
              {filteredTransactions.map((transaction) => {
                const isIncome = transaction.tipo === "entrada";
                return (
                  <div className="transaction-row" key={transaction.id}>
                    <span className={`transaction-icon ${isIncome ? "income" : "expense"}`}>
                      {isIncome ? <ArrowDownLeft size={18} /> : <ArrowUpRight size={18} />}
                    </span>
                    <span className="transaction-info">
                      <strong>{transaction.comentario || (isIncome ? "Receita" : "Despesa")}</strong>
                      <small>{transaction.categoria || "Sem categoria"} · {transaction.conta} · {formatDate(transaction.data)}</small>
                    </span>
                    <strong className={isIncome ? "amount-income" : "amount-expense"}>{isIncome ? "+" : "−"} {formatCurrency(transaction.valor)}</strong>
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
