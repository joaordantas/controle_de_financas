import { useEffect, useState } from "react";

import { Sidebar } from "./components/Sidebar";
import { AuthView } from "./views/AuthView";
import { CategoriesView } from "./views/CategoriesView";
import { DashboardView } from "./views/DashboardView";
import { FinanceView } from "./views/FinanceView";
import { ServicesView } from "./views/ServicesView";
import type { User, ViewKey } from "./types";

const STORAGE_KEY = "controle-financas-user";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [activeView, setActiveView] = useState<ViewKey>("dashboard");

  useEffect(() => {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return;
    }
    try {
      setUser(JSON.parse(raw) as User);
    } catch {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  function handleLogin(nextUser: User) {
    setUser(nextUser);
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextUser));
  }

  function handleLogout() {
    setUser(null);
    window.localStorage.removeItem(STORAGE_KEY);
  }

  if (!user) {
    return <AuthView onLogin={handleLogin} />;
  }

  return (
    <div className="app-shell">
      <Sidebar activeView={activeView} onChangeView={setActiveView} onLogout={handleLogout} user={user} />
      <main className="main-content">
        {activeView === "dashboard" ? <DashboardView user={user} /> : null}
        {activeView === "financeiro" ? <FinanceView user={user} /> : null}
        {activeView === "categorias" ? <CategoriesView user={user} /> : null}
        {activeView === "servicos" ? <ServicesView user={user} /> : null}
      </main>
    </div>
  );
}
