import type { RuleMetadata } from "@/hooks/use-rules";

export function parseMitreReferences(value: string | null | undefined): string[] {
  if (!value) return [];

  try {
    const parsed: unknown = JSON.parse(value);
    return Array.isArray(parsed) && parsed.every((item) => typeof item === "string") ? parsed : [];
  } catch {
    return value.split(",").map((reference) => reference.trim()).filter(Boolean);
  }
}

export function filterRules(rules: RuleMetadata[], query: string, severity: string, state: string) {
  const normalizedQuery = query.trim().toLowerCase();
  return rules.filter((rule) => {
    const matchesQuery = !normalizedQuery || [rule.name, rule.id, rule.description ?? "", rule.rule_type]
      .some((value) => value.toLowerCase().includes(normalizedQuery));
    const matchesSeverity = severity === "all" || rule.severity.toLowerCase() === severity;
    const matchesState = state === "all" || (state === "enabled" ? rule.enabled : !rule.enabled);
    return matchesQuery && matchesSeverity && matchesState;
  });
}

export function investigationStatusLabel(status: string) {
  const normalized = status.toLowerCase();
  if (normalized === "queued") return "Pending";
  if (normalized === "running") return "Running";
  if (normalized === "completed") return "Completed";
  if (normalized === "failed") return "Failed";
  if (normalized === "cancelled") return "Cancelled";
  return status;
}

export function predictionHasModelMetadata(modelName?: string, modelVersion?: string) {
  return Boolean(modelName && modelVersion);
}

export function formatTechniqueConfidence(probability?: number, score?: number) {
  if (probability !== undefined) return `Probability: ${(probability * 100).toFixed(0)}%`;
  if (score !== undefined) return `Model score: ${score}`;
  return "No numeric estimate supplied";
}

export function uniqueEvidenceReferences(...references: Array<string[] | undefined>) {
  return [...new Set(references.flatMap((items) => items ?? []).filter(Boolean))];
}
