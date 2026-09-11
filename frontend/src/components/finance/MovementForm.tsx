import { ArrowDownLeft, ArrowRight, ArrowRightLeft, ArrowUpRight, FolderPlus } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";

import type { Account, Category, MovementFormValues, MovementType } from "../../types";
import { Button } from "../ui/Button";

interface MovementFormProps {
  accounts: Account[];
  categories: Category[];
  initialValues: MovementFormValues;
  mode: "create" | "edit";
  onCreateCategory: (name: string) => Promise<Category>;
  onSubmit: (values: MovementFormValues) => Promise<void>;
  saving: boolean;
}

const typeOptions: Array<{ value: MovementType; label: string; icon: typeof ArrowUpRight }> = [
  { value: "saida", label: "Despesa", icon: ArrowUpRight },
  { value: "entrada", label: "Receita", icon: ArrowDownLeft },
  { value: "transferencia", label: "Transferência", icon: ArrowRightLeft },
];

export function MovementForm({
  accounts,
  categories,
  initialValues,
  mode,
  onCreateCategory,
  onSubmit,
  saving,
}: MovementFormProps) {
  const [values, setValues] = useState(initialValues);
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [categoryName, setCategoryName] = useState("");
  const [creatingCategory, setCreatingCategory] = useState(false);
  const [categoryError, setCategoryError] = useState("");

  const availableTypes = mode === "create"
    ? typeOptions
    : typeOptions.filter((option) => (
      initialValues.tipo === "transferencia"
        ? option.value === "transferencia"
        : option.value !== "transferencia"
    ));
  const isTransfer = values.tipo === "transferencia";
  const canSubmit = values.valor > 0
    && values.descricao.trim().length > 0
    && Boolean(values.data)
    && (isTransfer
      ? values.contaOrigemId > 0
        && values.contaDestinoId > 0
        && values.contaOrigemId !== values.contaDestinoId
      : Boolean(values.contaId));

  function update<K extends keyof MovementFormValues>(field: K, value: MovementFormValues[K]) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  function selectType(tipo: MovementType) {
    const primaryAccount = accounts.find((account) => account.principal) ?? accounts[0];
    const secondAccount = accounts.find((account) => account.id !== primaryAccount?.id);
    setValues((current) => ({
      ...current,
      tipo,
      contaId: tipo === "transferencia" ? null : current.contaId ?? primaryAccount?.id ?? null,
      contaOrigemId: current.contaOrigemId || primaryAccount?.id || 0,
      contaDestinoId: current.contaDestinoId || secondAccount?.id || 0,
    }));
  }

  async function handleCreateCategory() {
    if (!categoryName.trim()) return;
    try {
      setCreatingCategory(true);
      const category = await onCreateCategory(categoryName);
      update("categoriaId", category.id);
      setCategoryName("");
      setShowCategoryForm(false);
      setCategoryError("");
    } catch (error) {
      setCategoryError(error instanceof Error ? error.message : "Não foi possível criar a categoria.");
    } finally {
      setCreatingCategory(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (canSubmit) await onSubmit(values);
  }

  return (
    <form className="form-grid movement-form" onSubmit={handleSubmit}>
      <div className={`segmented-control movement-type-control ${availableTypes.length === 1 ? "single-option" : ""}`} aria-label="Tipo de movimentação">
        {availableTypes.map((option) => {
          const Icon = option.icon;
          return (
            <button className={values.tipo === option.value ? "is-active" : ""} key={option.value} onClick={() => selectType(option.value)} type="button">
              <Icon aria-hidden="true" size={17} />{option.label}
            </button>
          );
        })}
      </div>

      <label className="amount-field">
        <span>Valor</span>
        <div><span>R$</span><input autoFocus min="0.01" onChange={(event) => update("valor", Number(event.target.value))} step="0.01" type="number" value={values.valor || ""} /></div>
      </label>

      <label>
        Descrição
        <input maxLength={255} onChange={(event) => update("descricao", event.target.value)} placeholder={isTransfer ? "Ex.: Reserva do mês" : "Ex.: Mercado, salário, academia"} value={values.descricao} />
      </label>

      {isTransfer ? (
        accounts.length < 2 ? (
          <div className="inline-empty">
            <ArrowRightLeft aria-hidden="true" size={20} />
            <p>Você precisa de duas contas ativas. <Link to="/accounts">Gerenciar contas</Link></p>
          </div>
        ) : (
          <div className="transfer-accounts">
            <label>De<select onChange={(event) => update("contaOrigemId", Number(event.target.value))} value={values.contaOrigemId}>{accounts.map((account) => <option disabled={account.id === values.contaDestinoId} key={account.id} value={account.id}>{account.nome}</option>)}</select></label>
            <ArrowRight aria-hidden="true" size={20} />
            <label>Para<select onChange={(event) => update("contaDestinoId", Number(event.target.value))} value={values.contaDestinoId}>{accounts.map((account) => <option disabled={account.id === values.contaOrigemId} key={account.id} value={account.id}>{account.nome}</option>)}</select></label>
          </div>
        )
      ) : (
        <>
          <label>
            Categoria
            <select onChange={(event) => update("categoriaId", event.target.value ? Number(event.target.value) : null)} value={values.categoriaId ?? ""}>
              <option value="">Sem categoria</option>
              {categories.map((category) => <option key={category.id} value={category.id}>{category.nome}</option>)}
            </select>
          </label>
          {showCategoryForm ? (
            <div className="inline-category-form">
              <input aria-label="Nome da nova categoria" onChange={(event) => setCategoryName(event.target.value)} placeholder="Nome da categoria" value={categoryName} />
              <Button disabled={creatingCategory || !categoryName.trim()} onClick={() => void handleCreateCategory()} type="button" variant="secondary">Salvar</Button>
              <button className="text-button" onClick={() => setShowCategoryForm(false)} type="button">Cancelar</button>
              {categoryError ? <small className="field-error">{categoryError}</small> : null}
            </div>
          ) : (
            <button className="text-button add-category-button" onClick={() => setShowCategoryForm(true)} type="button"><FolderPlus size={15} />Criar categoria</button>
          )}
          <label>
            Conta
            <select onChange={(event) => update("contaId", event.target.value ? Number(event.target.value) : null)} value={values.contaId ?? ""}>
              <option value="">Selecione uma conta</option>
              {accounts.map((account) => <option key={account.id} value={account.id}>{account.nome}</option>)}
            </select>
          </label>
          {accounts.length === 0 ? <small className="field-hint">Adicione uma conta antes de registrar movimentações.</small> : null}
        </>
      )}

      <label>
        Data
        <input onChange={(event) => update("data", event.target.value)} type="date" value={values.data} />
      </label>

      <Button disabled={saving || !canSubmit} type="submit">
        {saving ? "Salvando..." : mode === "edit" ? "Salvar alterações" : isTransfer ? "Transferir" : "Adicionar movimentação"}
      </Button>
    </form>
  );
}
