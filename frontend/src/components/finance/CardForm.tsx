import { useState } from "react";
import type { FormEvent } from "react";

import type { CardFormValues } from "../../types";
import { Button } from "../ui/Button";

interface CardFormProps {
  initialValues?: CardFormValues;
  mode?: "create" | "edit";
  onSubmit: (values: CardFormValues) => Promise<void>;
  saving: boolean;
}

const defaults: CardFormValues = {
  nome: "",
  limiteTotal: 0,
  diaFechamento: 13,
  diaVencimento: 20,
};

export function CardForm({ initialValues = defaults, mode = "create", onSubmit, saving }: CardFormProps) {
  const [values, setValues] = useState(initialValues);

  function update<K extends keyof CardFormValues>(field: K, value: CardFormValues[K]) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (values.nome.trim() && values.limiteTotal > 0) await onSubmit(values);
  }

  return (
    <form className="form-grid" onSubmit={handleSubmit}>
      <label>Nome<input autoFocus={mode === "edit"} maxLength={60} onChange={(event) => update("nome", event.target.value)} placeholder="Ex.: Nubank" value={values.nome} /></label>
      <label className="amount-field"><span>Limite total</span><div><span>R$</span><input min="0.01" onChange={(event) => update("limiteTotal", Number(event.target.value))} step="0.01" type="number" value={values.limiteTotal || ""} /></div></label>
      <div className="two-column-fields">
        <label>Fecha no dia<input max="31" min="1" onChange={(event) => update("diaFechamento", Number(event.target.value))} type="number" value={values.diaFechamento} /></label>
        <label>Vence no dia<input max="31" min="1" onChange={(event) => update("diaVencimento", Number(event.target.value))} type="number" value={values.diaVencimento} /></label>
      </div>
      <Button disabled={saving || !values.nome.trim() || values.limiteTotal <= 0} type="submit">{saving ? "Salvando..." : mode === "edit" ? "Salvar alterações" : "Adicionar cartão"}</Button>
    </form>
  );
}
