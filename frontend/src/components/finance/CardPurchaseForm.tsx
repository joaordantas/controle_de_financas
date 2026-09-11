import { useState } from "react";
import type { FormEvent } from "react";

import type { Card, CardPurchaseFormValues, Category } from "../../types";
import { Button } from "../ui/Button";

interface CardPurchaseFormProps {
  cards: Card[];
  categories: Category[];
  initialValues: CardPurchaseFormValues;
  mode?: "create" | "edit";
  onSubmit: (values: CardPurchaseFormValues) => Promise<void>;
  saving: boolean;
}

export function CardPurchaseForm({ cards, categories, initialValues, mode = "create", onSubmit, saving }: CardPurchaseFormProps) {
  const [values, setValues] = useState(initialValues);

  function update<K extends keyof CardPurchaseFormValues>(field: K, value: CardPurchaseFormValues[K]) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (values.cartaoId && values.categoriaId && values.valor > 0 && values.descricao.trim() && values.data) await onSubmit(values);
  }

  return (
    <form className="form-grid" onSubmit={handleSubmit}>
      <label className="amount-field"><span>Valor</span><div><span>R$</span><input autoFocus min="0.01" onChange={(event) => update("valor", Number(event.target.value))} step="0.01" type="number" value={values.valor || ""} /></div></label>
      <label>Descrição<input maxLength={255} onChange={(event) => update("descricao", event.target.value)} placeholder="Ex.: iFood" value={values.descricao} /></label>
      <label>Categoria<select onChange={(event) => update("categoriaId", event.target.value ? Number(event.target.value) : null)} value={values.categoriaId ?? ""}><option value="">Selecione uma categoria</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.nome}</option>)}</select></label>
      <label>Cartão<select onChange={(event) => update("cartaoId", Number(event.target.value))} value={values.cartaoId}><option value={0}>Selecione um cartão</option>{cards.map((card) => <option key={card.id} value={card.id}>{card.nome} · disponível {card.limite_disponivel.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}</option>)}</select></label>
      <label>Data<input onChange={(event) => update("data", event.target.value)} type="date" value={values.data} /></label>
      <Button disabled={saving || !values.cartaoId || !values.categoriaId || values.valor <= 0 || !values.descricao.trim()} type="submit">{saving ? "Salvando..." : mode === "edit" ? "Salvar alterações" : "Adicionar compra"}</Button>
    </form>
  );
}
