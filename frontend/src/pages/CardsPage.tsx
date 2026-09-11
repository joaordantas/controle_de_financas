import { CalendarDays, CreditCard as CreditCardIcon, Eye, Pencil, Plus, Power, ReceiptText, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { useAuth } from "../app/providers";
import { CardForm } from "../components/finance/CardForm";
import { CardPurchaseForm } from "../components/finance/CardPurchaseForm";
import { Button } from "../components/ui/Button";
import { Card as SurfaceCard } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { Feedback } from "../components/ui/Feedback";
import { Modal } from "../components/ui/Modal";
import { PageHeader } from "../components/ui/PageHeader";
import { api } from "../services/api";
import type { Account, Card, CardFormValues, CardPurchase, CardPurchaseFormValues, Category, Invoice, InvoiceDetail, InvoiceStatus } from "../types";
import { formatCurrency, formatDate } from "../utils/formatters";

const statusLabels: Record<InvoiceStatus, string> = {
  aberta: "Aberta",
  fechada: "Fechada",
  paga: "Paga",
  vencida: "Vencida",
};

function invoiceLabel(invoice: Invoice) {
  const label = new Intl.DateTimeFormat("pt-BR", { month: "long", year: "numeric", timeZone: "UTC" }).format(new Date(Date.UTC(invoice.ano_referencia, invoice.mes_referencia - 1, 1)));
  return label.charAt(0).toUpperCase() + label.slice(1);
}

function purchaseDefaults(cards: Card[], preferredCardId?: number): CardPurchaseFormValues {
  const activeCards = cards.filter((card) => card.ativo);
  const selected = activeCards.find((card) => card.id === preferredCardId) ?? activeCards[0];
  return { cartaoId: selected?.id ?? 0, valor: 0, descricao: "", categoriaId: null, data: new Date().toISOString().slice(0, 10) };
}

export function CardsPage() {
  const { user } = useAuth();
  const [cards, setCards] = useState<Card[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [selectedCardId, setSelectedCardId] = useState(0);
  const [invoiceDetail, setInvoiceDetail] = useState<InvoiceDetail | null>(null);
  const [editingCard, setEditingCard] = useState<Card | null>(null);
  const [editingPurchase, setEditingPurchase] = useState<CardPurchase | null>(null);
  const [paymentAccountId, setPaymentAccountId] = useState(0);
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().slice(0, 10));
  const [cardFormVersion, setCardFormVersion] = useState(0);
  const [purchaseFormVersion, setPurchaseFormVersion] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const activeCards = useMemo(() => cards.filter((card) => card.ativo), [cards]);
  const activeAccounts = useMemo(() => accounts.filter((account) => account.ativo), [accounts]);
  const selectedCard = cards.find((card) => card.id === selectedCardId) ?? cards[0];

  async function load(preferredCardId?: number, detailId?: number) {
    if (!user) return;
    try {
      setLoading(true);
      const [cardData, categoryData, accountData] = await Promise.all([
        api.getCards(user.id, true),
        api.getCategories(user.id),
        api.getAccounts(user.id, true),
      ]);
      const cardId = cardData.some((card) => card.id === preferredCardId)
        ? preferredCardId as number
        : cardData.some((card) => card.id === selectedCardId)
          ? selectedCardId
          : cardData[0]?.id ?? 0;
      const invoiceData = cardId ? await api.getCardInvoices(cardId, user.id) : [];
      const detail = detailId ? await api.getInvoice(detailId, user.id) : null;
      setCards(cardData);
      setCategories(categoryData);
      setAccounts(accountData);
      setSelectedCardId(cardId);
      setInvoices(invoiceData);
      setInvoiceDetail(detail);
      const paymentAccounts = accountData.filter((account) => account.ativo);
      const primary = paymentAccounts.find((account) => account.principal) ?? paymentAccounts[0];
      setPaymentAccountId((current) => paymentAccounts.some((account) => account.id === current) ? current : primary?.id ?? 0);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível carregar seus cartões.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, [user?.id]);

  async function selectCard(cardId: number) {
    if (!user) return;
    setSelectedCardId(cardId);
    try {
      setInvoices(await api.getCardInvoices(cardId, user.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível carregar as faturas.");
    }
  }

  async function createCard(values: CardFormValues) {
    if (!user) return;
    try {
      setSaving(true);
      const created = await api.createCard({ usuario_id: user.id, nome: values.nome, limite_total: values.limiteTotal, dia_fechamento: values.diaFechamento, dia_vencimento: values.diaVencimento });
      setCardFormVersion((current) => current + 1);
      setMessage("Cartão adicionado com sucesso.");
      await load(created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível adicionar o cartão.");
      setMessage("");
    } finally {
      setSaving(false);
    }
  }

  async function updateCard(values: CardFormValues) {
    if (!user || !editingCard) return;
    try {
      setSaving(true);
      await api.updateCard(editingCard.id, { usuario_id: user.id, nome: values.nome, limite_total: values.limiteTotal, dia_fechamento: values.diaFechamento, dia_vencimento: values.diaVencimento });
      setEditingCard(null);
      setMessage("Cartão atualizado. Os ciclos já criados foram preservados.");
      await load(editingCard.id, invoiceDetail?.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível atualizar o cartão.");
      setMessage("");
    } finally {
      setSaving(false);
    }
  }

  async function toggleCard(card: Card) {
    if (!user || !window.confirm(`${card.ativo ? "Desativar" : "Reativar"} o cartão \"${card.nome}\"?`)) return;
    try {
      await api.updateCardStatus(card.id, user.id, !card.ativo);
      setMessage(card.ativo ? "Cartão desativado. O histórico foi mantido." : "Cartão reativado.");
      await load(card.id, invoiceDetail?.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível alterar o cartão.");
      setMessage("");
    }
  }

  async function createPurchase(values: CardPurchaseFormValues) {
    if (!user) return;
    try {
      setSaving(true);
      const purchase = await api.createCardPurchase({ usuario_id: user.id, cartao_id: values.cartaoId, valor: values.valor, descricao: values.descricao, categoria_id: values.categoriaId, data: values.data });
      setPurchaseFormVersion((current) => current + 1);
      setMessage("Compra adicionada à fatura correta.");
      await load(values.cartaoId, purchase.fatura_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível adicionar a compra.");
      setMessage("");
    } finally {
      setSaving(false);
    }
  }

  async function updatePurchase(values: CardPurchaseFormValues) {
    if (!user || !editingPurchase) return;
    try {
      setSaving(true);
      const updated = await api.updateCardPurchase(editingPurchase.id, { usuario_id: user.id, cartao_id: values.cartaoId, valor: values.valor, descricao: values.descricao, categoria_id: values.categoriaId, data: values.data });
      setEditingPurchase(null);
      setMessage("Compra atualizada e ciclo recalculado.");
      await load(updated.cartao_id, updated.fatura_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível atualizar a compra.");
      setMessage("");
    } finally {
      setSaving(false);
    }
  }

  async function deletePurchase(purchase: CardPurchase) {
    if (!user || !window.confirm(`Excluir a compra \"${purchase.descricao}\"?`)) return;
    try {
      await api.deleteCardPurchase(purchase.id, user.id);
      setMessage("Compra excluída e limite recalculado.");
      await load(purchase.cartao_id, purchase.fatura_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível excluir a compra.");
      setMessage("");
    }
  }

  async function openInvoice(invoiceId: number) {
    if (!user) return;
    try {
      setInvoiceDetail(await api.getInvoice(invoiceId, user.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível abrir a fatura.");
    }
  }

  async function payInvoice() {
    if (!user || !invoiceDetail || !paymentAccountId) return;
    if (!window.confirm(`Pagar ${formatCurrency(invoiceDetail.valor_total)} usando a conta selecionada?`)) return;
    try {
      setSaving(true);
      await api.payInvoice(invoiceDetail.id, user.id, paymentAccountId, paymentDate);
      setMessage("Fatura paga. O saldo da conta e o limite foram atualizados.");
      await load(invoiceDetail.cartao_id, invoiceDetail.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível pagar a fatura.");
      setMessage("");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page-stack">
      <PageHeader description="Acompanhe limite, compras e vencimentos sem calcular faturas manualmente." eyebrow="Planejamento financeiro" title="Cartões" />
      {error ? <Feedback>{error}</Feedback> : null}
      {message ? <Feedback tone="success">{message}</Feedback> : null}

      <section className="credit-card-grid" aria-label="Seus cartões">
        {loading ? [1, 2].map((item) => <span className="surface-card skeleton credit-card-skeleton" key={item} />) : null}
        {!loading && cards.length === 0 ? <SurfaceCard className="cards-empty"><EmptyState description="Cadastre um cartão para acompanhar faturas e limite disponível." icon={CreditCardIcon} title="Nenhum cartão cadastrado" /></SurfaceCard> : null}
        {!loading && cards.map((card) => (
          <SurfaceCard className={`credit-card-panel ${card.ativo ? "" : "credit-card-inactive"}`} key={card.id}>
            <div className="credit-card-heading"><span className="credit-card-icon"><CreditCardIcon size={20} /></span><div><small>{card.ativo ? "Cartão de crédito" : "Cartão inativo"}</small><h2>{card.nome}</h2></div><span className="card-inline-actions"><button aria-label={`Editar ${card.nome}`} className="icon-button" onClick={() => setEditingCard(card)} type="button"><Pencil size={15} /></button><button aria-label={`${card.ativo ? "Desativar" : "Reativar"} ${card.nome}`} className="icon-button" onClick={() => void toggleCard(card)} type="button"><Power size={15} /></button></span></div>
            <div className="credit-card-main"><span>Fatura atual</span><strong>{formatCurrency(card.fatura_atual?.valor_total ?? 0)}</strong></div>
            <div className="limit-row"><span>Disponível <strong>{formatCurrency(card.limite_disponivel)}</strong></span><span>Utilizado {card.percentual_utilizado.toLocaleString("pt-BR")}%</span></div>
            <div className="limit-track"><span style={{ width: `${Math.min(card.percentual_utilizado, 100)}%` }} /></div>
            <div className="credit-card-footer"><small>Fecha dia {card.dia_fechamento} · Vence dia {card.dia_vencimento}</small>{card.fatura_atual ? <Button onClick={() => void openInvoice(card.fatura_atual!.id)} type="button" variant="secondary"><Eye size={15} />Ver fatura</Button> : null}</div>
          </SurfaceCard>
        ))}
      </section>

      <div className="cards-forms-layout">
        <SurfaceCard as="section" className="card-form-panel"><div className="card-heading"><span className="section-kicker">Novo cartão</span><h2>Adicionar limite</h2></div><CardForm key={cardFormVersion} onSubmit={createCard} saving={saving} /></SurfaceCard>
        <SurfaceCard as="section" className="card-form-panel"><div className="card-heading"><span className="section-kicker">Registro rápido</span><h2>Nova compra</h2></div>{activeCards.length === 0 ? <div className="inline-empty"><ReceiptText size={20} /><p>Adicione ou reative um cartão antes de registrar compras.</p></div> : <CardPurchaseForm cards={activeCards} categories={categories} initialValues={purchaseDefaults(cards, selectedCardId)} key={`${purchaseFormVersion}-${selectedCardId}`} onSubmit={createPurchase} saving={saving} />}</SurfaceCard>
      </div>

      <SurfaceCard as="section" className="invoice-history-panel">
        <div className="card-heading card-heading-row"><div><span className="section-kicker">Ciclos</span><h2>Histórico de faturas</h2></div>{cards.length > 1 ? <select aria-label="Selecionar cartão do histórico" onChange={(event) => void selectCard(Number(event.target.value))} value={selectedCard?.id ?? 0}>{cards.map((card) => <option key={card.id} value={card.id}>{card.nome}</option>)}</select> : null}</div>
        {!selectedCard ? <EmptyState description="As faturas aparecerão depois que você adicionar um cartão." icon={CalendarDays} title="Sem histórico" /> : invoices.length === 0 ? <EmptyState description="O primeiro ciclo será criado automaticamente." icon={CalendarDays} title="Nenhuma fatura" /> : <div className="invoice-list">{invoices.map((invoice) => <button className="invoice-row" key={invoice.id} onClick={() => void openInvoice(invoice.id)} type="button"><span><strong>{invoiceLabel(invoice)}</strong><small>{invoice.quantidade_compras} {invoice.quantidade_compras === 1 ? "compra" : "compras"} · vence {formatDate(invoice.data_vencimento)}</small></span><strong>{formatCurrency(invoice.valor_total)}</strong><span className={`invoice-status ${invoice.status}`}>{statusLabels[invoice.status]}</span><Eye size={16} /></button>)}</div>}
      </SurfaceCard>

      {editingCard ? <Modal onClose={() => setEditingCard(null)} title="Editar cartão"><CardForm initialValues={{ nome: editingCard.nome, limiteTotal: editingCard.limite_total, diaFechamento: editingCard.dia_fechamento, diaVencimento: editingCard.dia_vencimento }} mode="edit" onSubmit={updateCard} saving={saving} /></Modal> : null}
      {editingPurchase ? <Modal onClose={() => setEditingPurchase(null)} title="Editar compra"><CardPurchaseForm cards={activeCards} categories={categories} initialValues={{ cartaoId: editingPurchase.cartao_id, valor: editingPurchase.valor, descricao: editingPurchase.descricao, categoriaId: editingPurchase.categoria_id, data: editingPurchase.data }} mode="edit" onSubmit={updatePurchase} saving={saving} /></Modal> : null}
      {invoiceDetail ? (
        <Modal onClose={() => setInvoiceDetail(null)} title={`Fatura ${invoiceLabel(invoiceDetail)}`}>
          <div className="invoice-detail-summary"><span className={`invoice-status ${invoiceDetail.status}`}>{statusLabels[invoiceDetail.status]}</span><strong>{formatCurrency(invoiceDetail.valor_total)}</strong><small>{formatDate(invoiceDetail.data_inicio)} até {formatDate(invoiceDetail.data_fechamento)} · vence {formatDate(invoiceDetail.data_vencimento)}</small></div>
          {invoiceDetail.compras.length === 0 ? <EmptyState description="Compras adicionadas a este ciclo aparecerão aqui." icon={ReceiptText} title="Fatura sem compras" /> : <div className="invoice-purchases">{invoiceDetail.compras.map((purchase) => <div className="invoice-purchase-row" key={purchase.id}><span><strong>{purchase.descricao}</strong><small>{purchase.categoria} · {formatDate(purchase.data)}</small></span><strong>{formatCurrency(purchase.valor)}</strong>{invoiceDetail.status !== "paga" ? <span className="row-actions"><button aria-label={`Editar ${purchase.descricao}`} className="icon-button" onClick={() => { setEditingPurchase(purchase); setInvoiceDetail(null); }} type="button"><Pencil size={14} /></button><button aria-label={`Excluir ${purchase.descricao}`} className="icon-button danger-icon-button" onClick={() => void deletePurchase(purchase)} type="button"><Trash2 size={14} /></button></span> : null}</div>)}</div>}
          {invoiceDetail.status === "paga" ? <Feedback tone="success">Paga em {invoiceDetail.data_pagamento ? formatDate(invoiceDetail.data_pagamento) : "data registrada"} pela conta {invoiceDetail.conta_pagamento}.</Feedback> : invoiceDetail.valor_total > 0 ? <div className="invoice-payment"><div className="card-heading"><span className="section-kicker">Pagamento integral</span><h2>Pagar fatura</h2></div>{activeAccounts.length === 0 ? <Feedback>Adicione uma conta ativa para pagar esta fatura.</Feedback> : <><label>Conta para pagamento<select onChange={(event) => setPaymentAccountId(Number(event.target.value))} value={paymentAccountId}>{activeAccounts.map((account) => <option key={account.id} value={account.id}>{account.nome}{account.principal ? " — Principal" : ""} · {formatCurrency(account.saldo_atual)}</option>)}</select></label><label>Data do pagamento<input onChange={(event) => setPaymentDate(event.target.value)} type="date" value={paymentDate} /></label><Button disabled={saving || !paymentAccountId} onClick={() => void payInvoice()} type="button">{saving ? "Pagando..." : `Pagar ${formatCurrency(invoiceDetail.valor_total)}`}</Button></>}</div> : null}
        </Modal>
      ) : null}
    </div>
  );
}
