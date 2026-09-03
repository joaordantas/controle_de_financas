import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { api } from "../api";
import type { Category, User } from "../types";

interface CategoriesViewProps {
  user: User;
}

export function CategoriesView({ user }: CategoriesViewProps) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [novaCategoria, setNovaCategoria] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingName, setEditingName] = useState("");
  const [error, setError] = useState("");

  async function load() {
    try {
      const data = await api.getCategories(user.id);
      setCategories(data);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel carregar as categorias.");
    }
  }

  useEffect(() => {
    void load();
  }, [user.id]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await api.createCategory(user.id, novaCategoria);
      setNovaCategoria("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar a categoria.");
    }
  }

  async function handleSave(categoriaId: number) {
    try {
      await api.updateCategory(categoriaId, user.id, editingName);
      setEditingId(null);
      setEditingName("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel atualizar a categoria.");
    }
  }

  async function handleDelete(categoriaId: number) {
    try {
      await api.deleteCategory(categoriaId, user.id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel remover a categoria.");
    }
  }

  return (
    <section className="content-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Organizacao</p>
          <h2>Categorias</h2>
        </div>
      </div>

      {error ? <p className="feedback error">{error}</p> : null}

      <div className="two-column">
        <form className="card form-grid" onSubmit={handleCreate}>
          <div className="section-title">
            <h3>Nova categoria</h3>
            <p>Exercicio direto de estado e envio de formulario.</p>
          </div>
          <label>
            Nome
            <input
              value={novaCategoria}
              onChange={(event) => setNovaCategoria(event.target.value)}
              placeholder="Ex: Alimentacao"
            />
          </label>
          <button className="primary-button" type="submit">
            Criar categoria
          </button>
        </form>

        <article className="card list-card">
          <div className="section-title">
            <h3>Suas categorias</h3>
            <p>Lista editavel para praticar renderizacao de arrays.</p>
          </div>

          {categories.length === 0 ? (
            <p className="empty-state">Crie sua primeira categoria.</p>
          ) : (
            <div className="stack-list">
              {categories.map((category) => (
                <div className="list-row" key={category.id}>
                  {editingId === category.id ? (
                    <input
                      value={editingName}
                      onChange={(event) => setEditingName(event.target.value)}
                    />
                  ) : (
                    <strong>{category.nome}</strong>
                  )}

                  <div className="row-actions">
                    {editingId === category.id ? (
                      <button className="ghost-button" onClick={() => void handleSave(category.id)} type="button">
                        Salvar
                      </button>
                    ) : (
                      <button
                        className="ghost-button"
                        onClick={() => {
                          setEditingId(category.id);
                          setEditingName(category.nome);
                        }}
                        type="button"
                      >
                        Editar
                      </button>
                    )}

                    <button
                      className="ghost-button danger"
                      onClick={() => void handleDelete(category.id)}
                      type="button"
                    >
                      Excluir
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </div>
    </section>
  );
}
