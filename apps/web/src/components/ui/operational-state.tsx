import type { ReactNode } from "react";
import { AlertTriangle, Inbox } from "lucide-react";
import { Button } from "@/components/ui/button";

type OperationalStateProps = {
  kind: "empty" | "error";
  title: string;
  description: string;
  action?: ReactNode;
};

export function OperationalState({ kind, title, description, action }: OperationalStateProps) {
  const Icon = kind === "error" ? AlertTriangle : Inbox;

  return (
    <section className={kind === "error" ? "soc-error-state" : "soc-empty-state"} aria-live="polite">
      <div className="max-w-md space-y-3">
        <Icon
          className={kind === "error" ? "mx-auto size-8 text-destructive" : "mx-auto size-8 text-muted-foreground"}
          aria-hidden="true"
        />
        <div>
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{description}</p>
        </div>
        {action ? <div className="pt-1">{action}</div> : null}
      </div>
    </section>
  );
}

export function RetryButton({ onClick, disabled }: { onClick: () => void; disabled?: boolean }) {
  return (
    <Button type="button" variant="outline" onClick={onClick} disabled={disabled}>
      Try again
    </Button>
  );
}
