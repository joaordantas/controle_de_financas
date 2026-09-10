import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLElement> {
  children: ReactNode;
  as?: "article" | "section" | "div";
}

export function Card({ as: Element = "article", children, className = "", ...props }: CardProps) {
  return (
    <Element className={`surface-card ${className}`.trim()} {...props}>
      {children}
    </Element>
  );
}
