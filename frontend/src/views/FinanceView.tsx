import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { api } from "../api";
import type { Category, Transaction, TransactionSummary, User } from "../types";

interface FinanceViewProps {
  user: User;
}

export function FinanceView({ user }: FinanceViewProps) {
  const today = new Date().toISOString().slice(0, 10);

  const [summary, setSummary] = useState<TransactionSummary>({ entradas: 0, saidas: 0, saldo: 0 });
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [valor, setValor] = useState(0);
  const [tipo, setTipo] = useState<"entrada" | "saida">("entrada");
  const [categoriaId, setCategoriaId] = useState<number | null>(null);
  const [comentario, setComentario] = useState("");
  const [data, setData] = useState(today);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    try {
      const [summaryData, transactionData, categoryData] = await Promise.all([
        api.getTransactionSummary(user.id),
        api.getTransactions(user.id),
        api.getCategories(user.id),
      ]);
      setSummary(summaryData);
      setTransactions(transactionData);
      setCategories(categoryData);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel carregar o financeiro.");
    }
  }

  useEffect(() => {
    void load();
  }, [user.id]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await api.createTransaction({
        usuario_id: user.id,
        valor,
        tipo,
        categoria_id: tipo === "saida" ? categoriaId : null,
        comentario,
        data,
      });
      setValor(0);
      setComentario("");
      setCategoriaId(null);
      setMessage("Transacao adicionada com sucesso.");
      setError("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel salvar a transacao.");
      setMessage("");
    }
  }

  return (
    <section className="content-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Fluxo financeiro</p>
          <h2>Financeiro</h2>
        </div>
      </div>

      {error ? <p className="feedback error">{error}</p> : null}
      {message ? <p className="feedback success">{message}</p> : null}

      <div className="metric-grid">
        <article className="metric-card">
          <span>Saldo</span>
          <strong>R$ {summary.saldo.toFixed(2)}</strong>
        </article>
        <article className="metric-card">
          <span>Entradas</span>
          <strong>R$ {summary.entradas.toFixed(2)}</strong>
        </article>
        <article className="metric-card">
          <span>Saidas</span>
          <strong>R$ {summary.saidas.toFixed(2)}</strong>
        </article>
      </div>

      <div className="two-column">
        <form className="card form-grid" onSubmit={handleSubmit}>
          <div className="section-title">
            <h3>Nova transacao</h3>
            <p>Exemplo pratico de formulario controlado com React.</p>
          </div>

          <label>
            Valor
            <input
              type="number"
              min="0"
              step="0.01"
              value={valor}
              onChange={(event) => setValor(Number(event.target.value))}
            />
          </label>

          <label>
            Tipo
            <select value={tipo} onChange={(event) => setTipo(event.target.value as "entrada" | "saida")}>
              <option value="entrada">entrada</option>
              <option value="saida">saida</option>
            </select>
          </label>

          {tipo === "saida" ? (
            <label>
              Categoria
              <select
                value={categoriaId ?? ""}
                onChange={(event) => setCategoriaId(event.target.value ? Number(event.target.value) : null)}
              >
                <option value="">Selecione</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.nome}
                  </option>
                ))}
              </select>
            </label>
          ) : null}

          <label>
            Comentario
            <input value={comentario} onChange={(event) => setComentario(event.target.value)} />
          </label>

          <label>
            Data
            <input type="date" value={data} onChange={(event) => setData(event.target.value)} />
          </label>

          <button className="primary-button" type="submit">
            Salvar transacao
          </button>
        </form>

        <article className="table-card">
          <div className="section-title">
            <h3>Historico</h3>
            <p>Use essa lista para revisar os dados vindos da API.</p>
          </div>
          {transactions.length === 0 ? (
            <p className="empty-state">Nenhuma transacao registrada ainda.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Valor</th>
                  <th>Tipo</th>
                  <th>Categoria</th>
                  <th>Comentario</th>
                  <th>Data</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td>R$ {transaction.valor.toFixed(2)}</td>
                    <td>{transaction.tipo}</td>
                    <td>{transaction.categoria}</td>
                    <td>{transaction.comentario ?? "-"}</td>
                    <td>{transaction.data}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </article>
      </div>
    </section>
  );
}
