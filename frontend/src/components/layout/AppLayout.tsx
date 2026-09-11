import { Moon, PiggyBank, Sun } from "lucide-react";
import { Outlet } from "react-router-dom";

import { MobileNavigation } from "./MobileNavigation";
import { Sidebar } from "./Sidebar";
import { useTheme } from "../../app/providers";

export function AppLayout() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-body">
        <header className="mobile-header">
          <div className="mobile-brand">
            <PiggyBank aria-hidden="true" size={21} />
            <strong>Nivra</strong>
          </div>
          <button aria-label={theme === "dark" ? "Ativar tema claro" : "Ativar tema escuro"} className="icon-button mobile-theme-button" onClick={toggleTheme} type="button">
            {theme === "dark" ? <Sun aria-hidden="true" size={18} /> : <Moon aria-hidden="true" size={18} />}
          </button>
        </header>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
      <MobileNavigation />
    </div>
  );
}
