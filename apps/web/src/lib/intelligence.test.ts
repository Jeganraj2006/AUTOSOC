import { describe, expect, it } from "vitest";
import type { RuleMetadata } from "@/hooks/use-rules";
import {
  filterRules,
  formatTechniqueConfidence,
  investigationStatusLabel,
  parseMitreReferences,
  predictionHasModelMetadata,
  uniqueEvidenceReferences,
} from "./intelligence";

const rule: RuleMetadata = {
  id: "bf7f00b4-a6fb-4b2e-8fc0-b8ad5dd99409",
  name: "Suspicious PowerShell",
  description: "Detects suspicious encoded PowerShell execution.",
  rule_type: "sigma",
  enabled: true,
  severity: "high",
  version: 2,
  mitre_references_json: '["T1059.001"]',
  created_at: "2026-10-26T10:00:00Z",
  updated_at: "2026-10-26T10:01:00Z",
};

describe("intelligence presentation helpers", () => {
  it("filters returned detection metadata without inventing server-side filters", () => {
    expect(filterRules([rule], "powershell", "high", "enabled")).toEqual([rule]);
    expect(filterRules([rule], "no match", "all", "all")).toEqual([]);
  });

  it("parses persisted ATT&CK references while tolerating legacy comma strings", () => {
    expect(parseMitreReferences(rule.mitre_references_json)).toEqual(["T1059.001"]);
    expect(parseMitreReferences("T1059.001, T1003")).toEqual(["T1059.001", "T1003"]);
    expect(parseMitreReferences("{bad json")).toEqual(["{bad json"]);
  });

  it("only labels estimates that the prediction API actually supplied", () => {
    expect(formatTechniqueConfidence(0.42)).toBe("Probability: 42%");
    expect(formatTechniqueConfidence(undefined, 9.4)).toBe("Model score: 9.4");
    expect(formatTechniqueConfidence()).toBe("No numeric estimate supplied");
    expect(predictionHasModelMetadata("Markov", "v1")).toBe(true);
    expect(predictionHasModelMetadata("Markov")).toBe(false);
  });

  it("presents persisted investigation states without simulating progress", () => {
    expect(investigationStatusLabel("queued")).toBe("Pending");
    expect(investigationStatusLabel("running")).toBe("Running");
    expect(investigationStatusLabel("failed")).toBe("Failed");
  });

  it("renders evidence citations once even when returned by multiple result fields", () => {
    expect(uniqueEvidenceReferences(["event:1", "alert:2"], ["alert:2", "source:3"])).toEqual(["event:1", "alert:2", "source:3"]);
  });
});
