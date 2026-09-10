import { SearchX } from "lucide-react";
import { Link } from "react-router-dom";

import { Card } from "../components/ui/Card";

export function NotFoundPage() {
  return (
    <Card className="coming-soon-card">
      <span className="coming-soon-icon"><SearchX size={26} /></span>
      <h1>Página não encontrada</h1>
      <p>O endereço acessado não existe nesta versão do produto.</p>
      <Link className="button button-primary" to="/dashboard">Voltar ao início</Link>
    </Card>
  );
}
