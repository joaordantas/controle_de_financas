import { PiggyBank } from "lucide-react";
import { Outlet } from "react-router-dom";

import { MobileNavigation } from "./MobileNavigation";
import { Sidebar } from "./Sidebar";

export function AppLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-body">
        <header className="mobile-header">
          <div className="mobile-brand">
            <PiggyBank aria-hidden="true" size={21} />
            <strong>Finanças</strong>
          </div>
          <span className="mobile-mode">Pessoal</span>
        </header>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
      <MobileNavigation />
    </div>
  );
}
