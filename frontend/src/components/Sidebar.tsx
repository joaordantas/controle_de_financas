import type { User, ViewKey } from "../types";

const labels: Record<ViewKey, string> = {
  dashboard: "Dashboard",
  financeiro: "Financeiro",
  categorias: "Categorias",
  servicos: "Servicos",
};

interface SidebarProps {
  activeView: ViewKey;
  onChangeView: (view: ViewKey) => void;
  onLogout: () => void;
  user: User;
}

export function Sidebar({ activeView, onChangeView, onLogout, user }: SidebarProps) {
  const views: ViewKey[] = ["dashboard", "financeiro", "categorias", "servicos"];

  return (
    <aside className="sidebar">
      <div className="brand">
        <p className="eyebrow">Controle de Financas</p>
        <h1>Nova Interface</h1>
      </div>

      <div className="user-card">
        <strong>{user.usuario}</strong>
        <span>{user.tipo_perfil}</span>
      </div>

      <nav className="nav-list">
        {views.map((view) => (
          <button
            key={view}
            className={view === activeView ? "nav-button active" : "nav-button"}
            onClick={() => onChangeView(view)}
          >
            {labels[view]}
          </button>
        ))}
      </nav>

      <button className="secondary-button" onClick={onLogout}>
        Sair
      </button>
    </aside>
  );
}
