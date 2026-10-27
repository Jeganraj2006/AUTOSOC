import type { ReactNode } from "react";

type PageHeaderProps = {
  title: string;
  description: string;
  breadcrumb?: string;
  actions?: ReactNode;
};

export function PageHeader({ title, description, breadcrumb, actions }: PageHeaderProps) {
  return (
    <header className="soc-page-header">
      <div className="min-w-0 space-y-2">
        {breadcrumb ? (
          <p className="text-xs font-medium text-muted-foreground">{breadcrumb}</p>
        ) : null}
        <div>
          <h1 className="text-2xl font-semibold tracking-[-0.025em] text-foreground sm:text-3xl">{title}</h1>
          <p className="mt-1 max-w-2xl text-sm leading-6 text-muted-foreground">{description}</p>
        </div>
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </header>
  );
}
