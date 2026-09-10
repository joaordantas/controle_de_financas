export interface User {
  id: number;
  usuario: string;
  email: string;
  tipo_perfil: string;
}

export interface Category {
  id: number;
  nome: string;
}

export interface Transaction {
  id: number;
  valor: number;
  tipo: string;
  categoria: string;
  comentario: string | null;
  data: string;
  conta_id: number | null;
  conta: string;
}

export type AccountType = "corrente" | "poupanca" | "digital" | "dinheiro" | "outro";

export interface Account {
  id: number;
  nome: string;
  tipo: AccountType;
  saldo_inicial: number;
  saldo_atual: number;
  ativo: boolean;
}

export interface Transfer {
  id: number;
  conta_origem_id: number;
  conta_origem: string;
  conta_destino_id: number;
  conta_destino: string;
  valor: number;
  descricao: string | null;
  data: string;
}

export interface TransactionSummary {
  entradas: number;
  saidas: number;
  saldo: number;
}

export interface ProfitSummary {
  entrada: number;
  saida: number;
  lucro: number;
}

export interface ReceivableByClient {
  cliente: string;
  valor_pendente: number;
}

export interface Sale {
  id: number;
  cliente: string;
  tipo: string;
  valor_total: number;
  comentario: string | null;
  data: string;
}

export interface Installment {
  id: number;
  venda_id: number;
  valor: number;
  status: string;
  data: string;
}

export interface ClientInstallmentsResponse {
  cliente: string;
  parcelas: Installment[];
  resumo: {
    total_pago: number;
    valor_total_vendas: number;
    ainda_falta: number;
  };
}
