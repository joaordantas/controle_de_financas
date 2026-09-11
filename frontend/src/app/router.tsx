import { Navigate, RouterProvider, createBrowserRouter } from "react-router-dom";
import type { ReactNode } from "react";

import { AppLayout } from "../components/layout/AppLayout";
import { ComingSoonPage } from "../pages/ComingSoonPage";
import { CardsPage } from "../pages/CardsPage";
import { DashboardPage } from "../pages/DashboardPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { SettingsPage } from "../pages/SettingsPage";
import { CategoriesPage } from "../pages/settings/CategoriesPage";
import { TransactionsPage } from "../pages/TransactionsPage";
import { AccountsPage } from "../pages/AccountsPage";
import { useAuth } from "./providers";

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate replace to="/login" />;
}

function PublicRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate replace to="/dashboard" /> : children;
}

const router = createBrowserRouter([
  {
    path: "/login",
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Navigate replace to="/dashboard" /> },
      { path: "dashboard", element: <DashboardPage /> },
      { path: "transactions", element: <TransactionsPage /> },
      { path: "accounts", element: <AccountsPage /> },
      { path: "cards", element: <CardsPage /> },
      {
        path: "budgets",
        element: <ComingSoonPage description="Os orçamentos por categoria serão adicionados na etapa de planejamento." title="Orçamentos" />,
      },
      {
        path: "goals",
        element: <ComingSoonPage description="As metas financeiras serão adicionadas depois do núcleo financeiro." title="Metas" />,
      },
      {
        path: "assistant",
        element: <ComingSoonPage description="A assistente financeira da Nivra está planejada e será conectada depois do motor de insights." title="Lumi" />,
      },
      { path: "settings", element: <SettingsPage /> },
      { path: "settings/categories", element: <CategoriesPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
