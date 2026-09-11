import type {
  Account,
  AccountType,
  Card,
  CardPurchase,
  Category,
  ClientInstallmentsResponse,
  Invoice,
  InvoiceDetail,
  ProfitSummary,
  ReceivableByClient,
  Sale,
  Transaction,
  TransactionSummary,
  Transfer,
  User,
} from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}/api${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = "Erro ao se comunicar com a API.";
    try {
      const body: { detail?: unknown } = await response.json();
      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body.detail)) {
        const messages = body.detail
          .map((item) => {
            if (typeof item === "string") return item;
            if (item && typeof item === "object" && "msg" in item && typeof item.msg === "string") return item.msg;
            return null;
          })
          .filter((message): message is string => Boolean(message));
        if (messages.length > 0) detail = messages.join(" ");
      }
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
  }) => request<Transaction>("/transactions", { method: "POST", body: JSON.stringify(payload) }),

  updateTransaction: (transactionId: number, payload: {
    usuario_id: number;
    valor: number;
    tipo: "entrada" | "saida";
    categoria_id: number | null;
    comentario: string;
    data: string;
    conta_id: number | null;
  }) => request<Transaction>(`/transactions/${transactionId}`, { method: "PUT", body: JSON.stringify(payload) }),

  deleteTransaction: (transactionId: number, usuarioId: number) =>
    request<void>(`/transactions/${transactionId}?usuario_id=${usuarioId}`, { method: "DELETE" }),

  getAccounts: (usuarioId: number, includeInactive = false) =>
    request<Account[]>(`/accounts?usuario_id=${usuarioId}&incluir_inativas=${includeInactive}`),

  createAccount: (payload: {
    usuario_id: number;
    nome: string;
    tipo: AccountType;
    saldo_inicial: number;
  }) => request<Account>("/accounts", { method: "POST", body: JSON.stringify(payload) }),

  updateAccount: (accountId: number, payload: {
    usuario_id: number;
    nome: string;
    tipo: AccountType;
    saldo_inicial: number;
  }) => request<Account>(`/accounts/${accountId}`, { method: "PUT", body: JSON.stringify(payload) }),

  updateAccountStatus: (accountId: number, usuarioId: number, ativo: boolean) =>
    request<Account>(`/accounts/${accountId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ usuario_id: usuarioId, ativo }),
    }),

  setPrimaryAccount: (accountId: number, usuarioId: number) =>
    request<Account>(`/accounts/${accountId}/primary`, {
      method: "PATCH",
      body: JSON.stringify({ usuario_id: usuarioId }),
    }),

  getTransfers: (usuarioId: number) =>
    request<Transfer[]>(`/transfers?usuario_id=${usuarioId}`),

  createTransfer: (payload: {
    usuario_id: number;
    conta_origem_id: number;
    conta_destino_id: number;
    valor: number;
    descricao: string;
    data: string;
  }) => request<Transfer>("/transfers", { method: "POST", body: JSON.stringify(payload) }),

  updateTransfer: (transferId: number, payload: {
    usuario_id: number;
    conta_origem_id: number;
    conta_destino_id: number;
    valor: number;
    descricao: string;
    data: string;
  }) => request<Transfer>(`/transfers/${transferId}`, { method: "PUT", body: JSON.stringify(payload) }),

  deleteTransfer: (transferId: number, usuarioId: number) =>
    request<void>(`/transfers/${transferId}?usuario_id=${usuarioId}`, { method: "DELETE" }),

  getCards: (usuarioId: number, includeInactive = true) =>
    request<Card[]>(`/cards?usuario_id=${usuarioId}&incluir_inativos=${includeInactive}`),

  createCard: (payload: { usuario_id: number; nome: string; limite_total: number; dia_fechamento: number; dia_vencimento: number }) =>
    request<Card>("/cards", { method: "POST", body: JSON.stringify(payload) }),

  updateCard: (cardId: number, payload: { usuario_id: number; nome: string; limite_total: number; dia_fechamento: number; dia_vencimento: number }) =>
    request<Card>(`/cards/${cardId}`, { method: "PUT", body: JSON.stringify(payload) }),

  updateCardStatus: (cardId: number, usuarioId: number, ativo: boolean) =>
    request<Card>(`/cards/${cardId}/status`, { method: "PATCH", body: JSON.stringify({ usuario_id: usuarioId, ativo }) }),

  getCardInvoices: (cardId: number, usuarioId: number) =>
    request<Invoice[]>(`/cards/${cardId}/invoices?usuario_id=${usuarioId}`),

  getInvoice: (invoiceId: number, usuarioId: number) =>
    request<InvoiceDetail>(`/invoices/${invoiceId}?usuario_id=${usuarioId}`),

  createCardPurchase: (payload: { usuario_id: number; cartao_id: number; valor: number; descricao: string; categoria_id: number | null; data: string }) =>
    request<CardPurchase>("/card-purchases", { method: "POST", body: JSON.stringify(payload) }),

  updateCardPurchase: (purchaseId: number, payload: { usuario_id: number; cartao_id: number; valor: number; descricao: string; categoria_id: number | null; data: string }) =>
    request<CardPurchase>(`/card-purchases/${purchaseId}`, { method: "PUT", body: JSON.stringify(payload) }),

  deleteCardPurchase: (purchaseId: number, usuarioId: number) =>
    request<void>(`/card-purchases/${purchaseId}?usuario_id=${usuarioId}`, { method: "DELETE" }),

  payInvoice: (invoiceId: number, usuarioId: number, accountId: number, paymentDate: string) =>
    request<InvoiceDetail>(`/invoices/${invoiceId}/pay`, {
      method: "POST",
      body: JSON.stringify({ usuario_id: usuarioId, conta_id: accountId, data: paymentDate }),
    }),

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
