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

  let styles = "bg-slate-950 text-slate-400 border-slate-800";
  let label = severity.toUpperCase();

  switch (normalized) {
    case "critical":
      styles = "bg-red-950/40 text-red-400 border-red-900/60 hover:bg-red-950/50";
      break;
    case "high":
      styles = "bg-orange-950/40 text-orange-400 border-orange-900/60 hover:bg-orange-950/50";
      break;
    case "medium":
      styles = "bg-yellow-950/40 text-yellow-400 border-yellow-900/60 hover:bg-yellow-950/50";
      break;
    case "low":
      styles = "bg-blue-950/40 text-blue-400 border-blue-900/60 hover:bg-blue-950/50";
      break;
    case "informational":
    case "info":
      styles = "bg-slate-900/60 text-slate-400 border-slate-800 hover:bg-slate-900/80";
      label = "INFO";
      break;
  }

  return (
    <Badge variant="outline" className={`font-mono text-xs font-semibold px-2 py-0.5 tracking-wider ${styles} ${className}`}>
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

  let dotColor = "bg-slate-500";
  let label = status.replace(/_/g, " ");
  let icon = <HelpCircle className="h-3.5 w-3.5 text-slate-400" />;

  switch (normalized) {
    case "new":
      dotColor = "bg-red-500";
      icon = <ShieldAlert className="h-3.5 w-3.5 text-red-500" />;
      break;
    case "triaged":
      dotColor = "bg-blue-500";
      icon = <Info className="h-3.5 w-3.5 text-blue-500" />;
      break;
    case "investigating":
      dotColor = "bg-yellow-500 animate-pulse";
      icon = <Clock className="h-3.5 w-3.5 text-yellow-500" />;
      break;
    case "awaiting approval":
      dotColor = "bg-purple-500";
      icon = <Clock className="h-3.5 w-3.5 text-purple-500" />;
      break;
    case "contained":
      dotColor = "bg-teal-500";
      icon = <CheckCircle2 className="h-3.5 w-3.5 text-teal-500" />;
      break;
    case "resolved":
    case "healthy":
      dotColor = "bg-emerald-500";
      icon = <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />;
      break;
    case "closed":
    case "disabled":
      dotColor = "bg-slate-600";
      icon = <CheckCircle2 className="h-3.5 w-3.5 text-slate-500" />;
      break;
    case "false positive":
      dotColor = "bg-slate-500";
      icon = <AlertCircle className="h-3.5 w-3.5 text-slate-400" />;
      break;
    case "warning":
      dotColor = "bg-orange-500";
      icon = <AlertTriangle className="h-3.5 w-3.5 text-orange-500" />;
      break;
    case "critical":
      dotColor = "bg-red-600";
      icon = <ShieldAlert className="h-3.5 w-3.5 text-red-600" />;
      break;
  }

  return (
    <div className={`inline-flex items-center gap-2 text-xs font-medium text-slate-300 ${className}`}>
      {showIcon ? (
        icon
      ) : (
        <span className={`h-2 w-2 rounded-full ${dotColor}`} />
      )}
      <span className="capitalize">{label}</span>
    </div>
  );
}
