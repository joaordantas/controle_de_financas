import { useEffect, useState } from "react";

import { api } from "../api";
import type { ProfitSummary, ReceivableByClient, User } from "../types";

interface DashboardViewProps {
  user: User;
}

export function DashboardView({ user }: DashboardViewProps) {
  const today = new Date().toISOString().slice(0, 10);
  const monthStart = `${today.slice(0, 8)}01`;

  const [dataInicio, setDataInicio] = useState(monthStart);
  const [dataFim, setDataFim] = useState(today);
  const [profit, setProfit] = useState<ProfitSummary>({ entrada: 0, saida: 0, lucro: 0 });
  const [receivableTotal, setReceivableTotal] = useState(0);
  const [receivables, setReceivables] = useState<ReceivableByClient[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [profitData, totalData, clientData] = await Promise.all([
          api.getProfit(user.id, dataInicio, dataFim),
          api.getReceivablesTotal(user.id),
          api.getReceivablesByClient(user.id),
        ]);
        setProfit(profitData);
        setReceivableTotal(totalData.total);
        setReceivables(clientData);
        setError("");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Nao foi possivel carregar o dashboard.");
      }
    }

    void load();
  }, [dataFim, dataInicio, user.id]);

  return (
    <section className="content-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Visao geral</p>
          <h2>Dashboard</h2>
        </div>
        <div className="date-filters">
          <label>
            De
            <input type="date" value={dataInicio} onChange={(event) => setDataInicio(event.target.value)} />
          </label>
          <label>
            Ate
            <input type="date" value={dataFim} onChange={(event) => setDataFim(event.target.value)} />
          </label>
        </div>
      </div>

      {error ? <p className="feedback error">{error}</p> : null}

      <div className="metric-grid">
        <article className="metric-card">
          <span>Entradas</span>
          <strong>R$ {profit.entrada.toFixed(2)}</strong>
        </article>
        <article className="metric-card">
          <span>Saidas</span>
          <strong>R$ {profit.saida.toFixed(2)}</strong>
        </article>
        <article className="metric-card">
          <span>Lucro</span>
          <strong>R$ {profit.lucro.toFixed(2)}</strong>
        </article>
        <article className="metric-card accent">
          <span>Total a receber</span>
          <strong>R$ {receivableTotal.toFixed(2)}</strong>
        </article>
      </div>

      <article className="table-card">
        <div className="section-title">
          <h3>A receber por cliente</h3>
          <p>Lista de parcelas pendentes por cliente.</p>
        </div>

        {receivables.length === 0 ? (
          <p className="empty-state">Nenhuma parcela pendente no momento.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Valor pendente</th>
              </tr>
            </thead>
            <tbody>
              {receivables.map((item) => (
                <tr key={item.cliente}>
                  <td>{item.cliente}</td>
                  <td>R$ {item.valor_pendente.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </article>
    </section>
  );
}
