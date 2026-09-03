import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { api } from "../api";
import type { ClientInstallmentsResponse, Sale, User } from "../types";

interface ServicesViewProps {
  user: User;
}

export function ServicesView({ user }: ServicesViewProps) {
  const today = new Date().toISOString().slice(0, 10);

  const [sales, setSales] = useState<Sale[]>([]);
  const [clients, setClients] = useState<string[]>([]);
  const [installmentsByClient, setInstallmentsByClient] = useState<ClientInstallmentsResponse | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [cliente, setCliente] = useState("");
  const [tipo, setTipo] = useState("Manutencao");
  const [valorTotal, setValorTotal] = useState(0);
  const [comentario, setComentario] = useState("");
  const [dataVenda, setDataVenda] = useState(today);

  const [clienteSelecionado, setClienteSelecionado] = useState("");
  const [vendaId, setVendaId] = useState<number>(0);
  const [quantidade, setQuantidade] = useState(1);
  const [valorParcela, setValorParcela] = useState(0);
  const [statusInicial, setStatusInicial] = useState<"pendente" | "pago">("pendente");
  const [dataParcela, setDataParcela] = useState(today);
  const [parcelaId, setParcelaId] = useState(0);

  async function load() {
    try {
      const [salesData, clientsData] = await Promise.all([api.getSales(user.id), api.getClients(user.id)]);
      setSales(salesData);
      setClients(clientsData);
      if (!clienteSelecionado && clientsData.length > 0) {
        setClienteSelecionado(clientsData[0]);
      }
      if (!vendaId && salesData.length > 0) {
        setVendaId(salesData[0].id);
      }
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel carregar os servicos.");
    }
  }

  useEffect(() => {
    void load();
  }, [user.id]);

  async function handleCreateSale(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await api.createSale({
        usuario_id: user.id,
        cliente,
        tipo,
        valor_total: valorTotal,
        comentario,
        data: dataVenda,
      });
      setCliente("");
      setValorTotal(0);
      setComentario("");
      setMessage("Venda cadastrada com sucesso.");
      setError("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar a venda.");
      setMessage("");
    }
  }

  async function handleCreateInstallments(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await api.createInstallments({
        usuario_id: user.id,
        venda_id: vendaId,
        quantidade,
        valor: valorParcela,
        status: statusInicial,
        data: dataParcela,
      });
      setMessage("Parcelas adicionadas com sucesso.");
      setError("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar as parcelas.");
      setMessage("");
    }
  }

  async function handleSearchClient() {
    try {
      const data = await api.getInstallmentsByClient(user.id, clienteSelecionado);
      setInstallmentsByClient(data);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel consultar parcelas.");
    }
  }

  async function handlePayInstallment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      const response = await api.payInstallment(parcelaId, user.id);
      setMessage(response.message);
      setError("");
      await load();
      if (clienteSelecionado) {
        await handleSearchClient();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel registrar o pagamento.");
      setMessage("");
    }
  }

  return (
    <section className="content-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Servicos e vendas</p>
          <h2>Servicos</h2>
        </div>
      </div>

      {error ? <p className="feedback error">{error}</p> : null}
      {message ? <p className="feedback success">{message}</p> : null}

      <div className="three-column">
        <form className="card form-grid" onSubmit={handleCreateSale}>
          <div className="section-title">
            <h3>Nova venda</h3>
            <p>Consome a rota POST de vendas.</p>
          </div>
          <label>
            Cliente
            <input value={cliente} onChange={(event) => setCliente(event.target.value)} />
          </label>
          <label>
            Tipo
            <select value={tipo} onChange={(event) => setTipo(event.target.value)}>
              <option>Manutencao</option>
              <option>Venda</option>
              <option>Emprestimo</option>
            </select>
          </label>
          <label>
            Valor total
            <input
              type="number"
              min="0"
              step="0.01"
              value={valorTotal}
              onChange={(event) => setValorTotal(Number(event.target.value))}
            />
          </label>
          <label>
            Comentario
            <input value={comentario} onChange={(event) => setComentario(event.target.value)} />
          </label>
          <label>
            Data
            <input type="date" value={dataVenda} onChange={(event) => setDataVenda(event.target.value)} />
          </label>
          <button className="primary-button" type="submit">
            Cadastrar venda
          </button>
        </form>

        <form className="card form-grid" onSubmit={handleCreateInstallments}>
          <div className="section-title">
            <h3>Parcelas</h3>
            <p>Valida para nao ultrapassar o valor da venda.</p>
          </div>
          <label>
            Venda
            <select value={vendaId} onChange={(event) => setVendaId(Number(event.target.value))}>
              {sales.map((sale) => (
                <option key={sale.id} value={sale.id}>
                  #{sale.id} - {sale.cliente}
                </option>
              ))}
            </select>
          </label>
          <label>
            Quantidade
            <input
              type="number"
              min="1"
              value={quantidade}
              onChange={(event) => setQuantidade(Number(event.target.value))}
            />
          </label>
          <label>
            Valor da parcela
            <input
              type="number"
              min="0"
              step="0.01"
              value={valorParcela}
              onChange={(event) => setValorParcela(Number(event.target.value))}
            />
          </label>
          <label>
            Status inicial
            <select
              value={statusInicial}
              onChange={(event) => setStatusInicial(event.target.value as "pendente" | "pago")}
            >
              <option value="pendente">pendente</option>
              <option value="pago">pago</option>
            </select>
          </label>
          <label>
            Data
            <input type="date" value={dataParcela} onChange={(event) => setDataParcela(event.target.value)} />
          </label>
          <button className="primary-button" type="submit">
            Adicionar parcelas
          </button>
        </form>

        <div className="stack-panel">
          <article className="card form-grid">
            <div className="section-title">
              <h3>Consultar cliente</h3>
              <p>Busca as parcelas pela API.</p>
            </div>
            <label>
              Cliente
              <select
                value={clienteSelecionado}
                onChange={(event) => setClienteSelecionado(event.target.value)}
              >
                {clients.map((client) => (
                  <option key={client} value={client}>
                    {client}
                  </option>
                ))}
              </select>
            </label>
            <button className="secondary-button" onClick={() => void handleSearchClient()} type="button">
              Buscar parcelas
            </button>
          </article>

          <form className="card form-grid" onSubmit={handlePayInstallment}>
            <div className="section-title">
              <h3>Registrar pagamento</h3>
              <p>Usa o fluxo atomico do backend.</p>
            </div>
            <label>
              ID da parcela
              <input
                type="number"
                min="1"
                value={parcelaId}
                onChange={(event) => setParcelaId(Number(event.target.value))}
              />
            </label>
            <button className="primary-button" type="submit">
              Marcar como paga
            </button>
          </form>
        </div>
      </div>

      <article className="table-card">
        <div className="section-title">
          <h3>Vendas cadastradas</h3>
          <p>Referencia visual para comparar com o Streamlit.</p>
        </div>
        {sales.length === 0 ? (
          <p className="empty-state">Nenhuma venda cadastrada ainda.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Cliente</th>
                <th>Tipo</th>
                <th>Valor</th>
                <th>Data</th>
              </tr>
            </thead>
            <tbody>
              {sales.map((sale) => (
                <tr key={sale.id}>
                  <td>{sale.id}</td>
                  <td>{sale.cliente}</td>
                  <td>{sale.tipo}</td>
                  <td>R$ {sale.valor_total.toFixed(2)}</td>
                  <td>{sale.data}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </article>

      {installmentsByClient ? (
        <article className="table-card">
          <div className="section-title">
            <h3>Parcelas de {installmentsByClient.cliente}</h3>
            <p>
              Total pago: R$ {installmentsByClient.resumo.total_pago.toFixed(2)} | Falta: R${" "}
              {installmentsByClient.resumo.ainda_falta.toFixed(2)}
            </p>
          </div>
          {installmentsByClient.parcelas.length === 0 ? (
            <p className="empty-state">Nenhuma parcela encontrada para este cliente.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Venda</th>
                  <th>Valor</th>
                  <th>Status</th>
                  <th>Data</th>
                </tr>
              </thead>
              <tbody>
                {installmentsByClient.parcelas.map((installment) => (
                  <tr key={installment.id}>
                    <td>{installment.id}</td>
                    <td>{installment.venda_id}</td>
                    <td>R$ {installment.valor.toFixed(2)}</td>
                    <td>{installment.status}</td>
                    <td>{installment.data}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </article>
      ) : null}
    </section>
  );
}
