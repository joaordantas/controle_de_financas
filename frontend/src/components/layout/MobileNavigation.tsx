import { MoreHorizontal, Plus } from "lucide-react";
import { NavLink } from "react-router-dom";

import { mobileNavigation } from "./navigation";

export function MobileNavigation() {
  return (
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

      <NavLink aria-label="Adicionar transação" className="mobile-add-button" to="/transactions?new=1#new-transaction">
        <Plus aria-hidden="true" size={27} strokeWidth={2.2} />
      </NavLink>

      {mobileNavigation.slice(2).map((item) => {
        const Icon = item.label === "Mais" ? MoreHorizontal : item.icon;
        return (
          <NavLink className={({ isActive }) => `mobile-nav-link${isActive ? " is-active" : ""}`} key={item.path} to={item.path}>
            <Icon aria-hidden="true" size={21} />
            <span>{item.label}</span>
          </NavLink>
        );
      })}
    </nav>
  );
}
