import type {
  Account,
  AccountType,
  Category,
  ClientInstallmentsResponse,
  ProfitSummary,
  ReceivableByClient,
  Sale,
  Transaction,
  TransactionSummary,
  Transfer,
  User,
} from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = "Erro ao se comunicar com a API.";
    try {
      const body = await response.json();
      if (body.detail) detail = body.detail;
    } catch {
      detail = response.statusText || detail;
    }
    throw new Error(detail);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  login: (email: string, senha: string) =>
    request<User>("/auth/login", { method: "POST", body: JSON.stringify({ email, senha }) }),

  register: (payload: { usuario: string; email: string; senha: string; tipo_perfil: string }) =>
    request<User>("/auth/register", { method: "POST", body: JSON.stringify(payload) }),

  getCategories: (usuarioId: number) =>
    request<Category[]>(`/categories?usuario_id=${usuarioId}`),

  createCategory: (usuarioId: number, nome: string) =>
    request<Category>("/categories", {
      method: "POST",
      body: JSON.stringify({ usuario_id: usuarioId, nome }),
    }),

  updateCategory: (categoriaId: number, usuarioId: number, nome: string) =>
    request<Category>(`/categories/${categoriaId}`, {
      method: "PUT",
      body: JSON.stringify({ usuario_id: usuarioId, nome }),
    }),

  deleteCategory: (categoriaId: number, usuarioId: number) =>
    request<void>(`/categories/${categoriaId}?usuario_id=${usuarioId}`, { method: "DELETE" }),

  getTransactions: (usuarioId: number) =>
    request<Transaction[]>(`/transactions?usuario_id=${usuarioId}`),

  getTransactionSummary: (usuarioId: number) =>
    request<TransactionSummary>(`/transactions/summary?usuario_id=${usuarioId}`),

  createTransaction: (payload: {
    usuario_id: number;
    valor: number;
    tipo: "entrada" | "saida";
    categoria_id: number | null;
    comentario: string;
    data: string;
    conta_id: number | null;
  }) => request("/transactions", { method: "POST", body: JSON.stringify(payload) }),

  getAccounts: (usuarioId: number) =>
    request<Account[]>(`/accounts?usuario_id=${usuarioId}`),

  createAccount: (payload: {
    usuario_id: number;
    nome: string;
    tipo: AccountType;
    saldo_inicial: number;
  }) => request<Account>("/accounts", { method: "POST", body: JSON.stringify(payload) }),

  getTransfers: (usuarioId: number) =>
    request<Transfer[]>(`/transfers?usuario_id=${usuarioId}`),

  createTransfer: (payload: {
    usuario_id: number;
    conta_origem_id: number;
    conta_destino_id: number;
    valor: number;
    descricao: string;
    data: string;
  }) => request("/transfers", { method: "POST", body: JSON.stringify(payload) }),

  getProfit: (usuarioId: number, dataInicio: string, dataFim: string) =>
    request<ProfitSummary>(`/dashboard/profit?usuario_id=${usuarioId}&data_inicio=${dataInicio}&data_fim=${dataFim}`),

  getReceivablesTotal: (usuarioId: number) =>
    request<{ total: number }>(`/dashboard/receivables/total?usuario_id=${usuarioId}`),

  getReceivablesByClient: (usuarioId: number) =>
    request<ReceivableByClient[]>(`/dashboard/receivables/by-client?usuario_id=${usuarioId}`),

  getSales: (usuarioId: number) => request<Sale[]>(`/sales?usuario_id=${usuarioId}`),

  createSale: (payload: {
    usuario_id: number;
    cliente: string;
    tipo: string;
    valor_total: number;
    comentario: string;
    data: string;
  }) => request<Sale>("/sales", { method: "POST", body: JSON.stringify(payload) }),

  getClients: (usuarioId: number) => request<string[]>(`/sales/clients?usuario_id=${usuarioId}`),

  getInstallmentsByClient: (usuarioId: number, cliente: string) =>
    request<ClientInstallmentsResponse>(`/installments/by-client?usuario_id=${usuarioId}&cliente=${encodeURIComponent(cliente)}`),

  createInstallments: (payload: {
    usuario_id: number;
    venda_id: number;
    quantidade: number;
    valor: number;
    status: "pendente" | "pago";
    data: string;
  }) => request("/installments", { method: "POST", body: JSON.stringify(payload) }),

  payInstallment: (parcelaId: number, usuarioId: number) =>
    request<{ message: string }>(`/installments/${parcelaId}/pay?usuario_id=${usuarioId}`, { method: "POST" }),
};
