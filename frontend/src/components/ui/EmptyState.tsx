import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ action, description, icon: Icon, title }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <span className="empty-state-icon"><Icon aria-hidden="true" size={22} /></span>
      <strong>{title}</strong>
      <p>{description}</p>
      {action}
    </div>
  );
}
