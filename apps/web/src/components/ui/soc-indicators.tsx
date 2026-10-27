import React from "react";
import { Badge } from "@/components/ui/badge";
import { 
  AlertCircle, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  HelpCircle, 
  Info, 
  ShieldAlert 
} from "lucide-react";

// Severity visual definitions
export type SeverityType = "critical" | "high" | "medium" | "low" | "informational" | string;

export interface SeverityBadgeProps {
  severity: SeverityType;
  className?: string;
}

export function SeverityBadge({ severity, className = "" }: SeverityBadgeProps) {
  const normalized = severity.toLowerCase();

  let styles = "bg-muted text-muted-foreground border-border";
  let label = severity.toUpperCase();

  switch (normalized) {
    case "critical":
      styles = "bg-destructive/15 text-destructive border-destructive/35";
      break;
    case "high":
      styles = "bg-orange-500/15 text-orange-500 border-orange-500/35";
      break;
    case "medium":
      styles = "bg-amber-500/15 text-amber-500 border-amber-500/35";
      break;
    case "low":
      styles = "bg-primary/15 text-primary border-primary/35";
      break;
    case "informational":
    case "info":
      styles = "bg-muted text-muted-foreground border-border";
      label = "INFO";
      break;
  }

  return (
    <Badge variant="outline" className={`px-2 py-0.5 text-xs font-semibold tracking-wide ${styles} ${className}`}>
      {label}
    </Badge>
  );
}

// Status visual definitions
export type StatusType = 
  | "new" 
  | "triaged" 
  | "investigating" 
  | "awaiting_approval" 
  | "contained" 
  | "resolved" 
  | "closed" 
  | "false_positive"
  | "healthy"
  | "warning"
  | "critical"
  | "disabled"
  | string;

export interface StatusIndicatorProps {
  status: StatusType;
  showIcon?: boolean;
  className?: string;
}

export function StatusIndicator({ status, showIcon = true, className = "" }: StatusIndicatorProps) {
  const normalized = status.toLowerCase().replace(/_/g, " ");

  let dotColor = "bg-muted-foreground";
  const label = status.replace(/_/g, " ");
  let icon = <HelpCircle className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />;

  switch (normalized) {
    case "new":
      dotColor = "bg-red-500";
      icon = <ShieldAlert className="h-3.5 w-3.5 text-destructive" aria-hidden="true" />;
      break;
    case "triaged":
      dotColor = "bg-blue-500";
      icon = <Info className="h-3.5 w-3.5 text-primary" aria-hidden="true" />;
      break;
    case "investigating":
      dotColor = "bg-yellow-500 animate-pulse";
      icon = <Clock className="h-3.5 w-3.5 text-amber-500" aria-hidden="true" />;
      break;
    case "awaiting approval":
      dotColor = "bg-purple-500";
      icon = <Clock className="h-3.5 w-3.5 text-violet-500" aria-hidden="true" />;
      break;
    case "contained":
      dotColor = "bg-teal-500";
      icon = <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" aria-hidden="true" />;
      break;
    case "resolved":
    case "healthy":
      dotColor = "bg-emerald-500";
      icon = <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" aria-hidden="true" />;
      break;
    case "closed":
    case "disabled":
      dotColor = "bg-slate-600";
      icon = <CheckCircle2 className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />;
      break;
    case "false positive":
      dotColor = "bg-slate-500";
      icon = <AlertCircle className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />;
      break;
    case "warning":
      dotColor = "bg-orange-500";
      icon = <AlertTriangle className="h-3.5 w-3.5 text-amber-500" aria-hidden="true" />;
      break;
    case "critical":
      dotColor = "bg-red-600";
      icon = <ShieldAlert className="h-3.5 w-3.5 text-destructive" aria-hidden="true" />;
      break;
  }

  return (
    <div className={`inline-flex items-center gap-2 text-xs font-medium text-foreground ${className}`}>
      {showIcon ? (
        icon
      ) : (
        <span className={`h-2 w-2 rounded-full ${dotColor}`} />
      )}
      <span className="capitalize">{label}</span>
    </div>
  );
}
