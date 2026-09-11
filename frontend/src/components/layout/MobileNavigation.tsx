import { MoreHorizontal, Plus, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

import { mobileMoreFinanceNavigation, mobileMoreSettingsNavigation, mobileNavigation } from "./navigation";

export function MobileNavigation() {
  const location = useLocation();
  const [moreOpen, setMoreOpen] = useState(false);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const moreButtonRef = useRef<HTMLButtonElement>(null);
  const moreIsActive = [...mobileMoreFinanceNavigation, ...mobileMoreSettingsNavigation]
    .some((item) => location.pathname === item.path || location.pathname.startsWith(`${item.path}/`));

  useEffect(() => {
    setMoreOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!moreOpen) return;

    closeButtonRef.current?.focus();
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMoreOpen(false);
        requestAnimationFrame(() => moreButtonRef.current?.focus());
      }
    }
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [moreOpen]);

  return (
    <>
      {moreOpen ? (
        <>
          <button aria-label="Fechar menu Mais" className="mobile-more-backdrop" onClick={() => setMoreOpen(false)} type="button" />
          <section aria-labelledby="mobile-more-title" aria-modal="true" className="mobile-more-sheet" role="dialog">
            <header className="mobile-more-header">
              <h2 id="mobile-more-title">Mais</h2>
              <button aria-label="Fechar menu Mais" className="icon-button" onClick={() => setMoreOpen(false)} ref={closeButtonRef} type="button">
                <X aria-hidden="true" size={20} />
              </button>
            </header>

            <nav aria-label="Finanças" className="mobile-more-group">
              <span className="navigation-label">Finanças</span>
              {mobileMoreFinanceNavigation.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink className={({ isActive }) => `mobile-more-link${isActive ? " is-active" : ""}`} key={item.path} onClick={() => setMoreOpen(false)} to={item.path}>
                    <Icon aria-hidden="true" size={20} />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </nav>

            <nav aria-label="Configurações" className="mobile-more-group">
              <span className="navigation-label">Configurações</span>
              {mobileMoreSettingsNavigation.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink className={({ isActive }) => `mobile-more-link${isActive ? " is-active" : ""}`} key={item.path} onClick={() => setMoreOpen(false)} to={item.path}>
                    <Icon aria-hidden="true" size={20} />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </nav>
          </section>
        </>
      ) : null}

      <nav aria-label="Navegação mobile" className="mobile-navigation">
        {mobileNavigation.slice(0, 2).map((item) => {
          const Icon = item.icon;
          return (
            <NavLink className={({ isActive }) => `mobile-nav-link${isActive ? " is-active" : ""}`} key={item.path} to={item.path}>
              <Icon aria-hidden="true" size={21} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}

        <span aria-hidden="true" className="mobile-nav-spacer" />
        <NavLink aria-label="Adicionar transação" className="mobile-add-button" to="/transactions?new=1#new-transaction">
          <Plus aria-hidden="true" size={27} strokeWidth={2.2} />
        </NavLink>

        {mobileNavigation.slice(2).map((item) => {
          const Icon = item.icon;
          return (
            <NavLink className={({ isActive }) => `mobile-nav-link${isActive ? " is-active" : ""}`} key={item.path} to={item.path}>
              <Icon aria-hidden="true" size={21} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}

        <button aria-expanded={moreOpen} aria-haspopup="dialog" className={`mobile-nav-link mobile-nav-more-button${moreIsActive || moreOpen ? " is-active" : ""}`} onClick={() => setMoreOpen((open) => !open)} ref={moreButtonRef} type="button">
          <MoreHorizontal aria-hidden="true" size={21} />
          <span>Mais</span>
        </button>
      </nav>
    </>
  );
}
