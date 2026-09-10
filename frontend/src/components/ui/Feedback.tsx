import { AlertCircle, CheckCircle2 } from "lucide-react";

interface FeedbackProps {
  children: string;
  tone?: "error" | "success";
}

export function Feedback({ children, tone = "error" }: FeedbackProps) {
  const Icon = tone === "success" ? CheckCircle2 : AlertCircle;

  return (
    <div className={`feedback feedback-${tone}`} role={tone === "error" ? "alert" : "status"}>
      <Icon aria-hidden="true" size={18} />
      <span>{children}</span>
    </div>
  );
}
