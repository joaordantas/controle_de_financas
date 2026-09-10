import { ArrowLeft, Construction } from "lucide-react";
import { Link } from "react-router-dom";

import { Card } from "../components/ui/Card";
import { PageHeader } from "../components/ui/PageHeader";

interface ComingSoonPageProps {
  title: string;
  description: string;
}

export function ComingSoonPage({ description, title }: ComingSoonPageProps) {
  return (
    <div className="page-stack">
      <PageHeader description="Esta área já tem um lugar definido na nova navegação." eyebrow="Próximas etapas" title={title} />
      <Card className="coming-soon-card">
        <span className="coming-soon-icon"><Construction aria-hidden="true" size={26} /></span>
        <h2>Em breve</h2>
        <p>{description}</p>
        <Link className="button button-secondary" to="/dashboard"><ArrowLeft size={17} />Voltar ao início</Link>
      </Card>
    </div>
  );
}
