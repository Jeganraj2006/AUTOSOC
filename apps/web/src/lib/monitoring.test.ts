import { describe, expect, it } from "vitest";
import {
  buildEventQuery,
  canExecuteApprovedDryRun,
  canManageTriage,
  incidentHref,
  isActiveAlertStatus,
} from "./monitoring";

describe("monitoring workspace helpers", () => {
  it("uses only event filters supported by the current API contract", () => {
    expect(buildEventQuery("all", "  ", 50)).toEqual({
      category: undefined,
      source_ip: undefined,
      limit: 50,
    });
    expect(buildEventQuery("authentication", " 203.0.113.9 ", 100)).toEqual({
      category: "authentication",
      source_ip: "203.0.113.9",
      limit: 100,
    });
  });

  it("keeps alert posture counts limited to unresolved records", () => {
    expect(isActiveAlertStatus("new")).toBe(true);
    expect(isActiveAlertStatus("investigating")).toBe(true);
    expect(isActiveAlertStatus("resolved")).toBe(false);
    expect(isActiveAlertStatus("false_positive")).toBe(false);
  });

  it("keeps mutations hidden from viewer roles", () => {
    expect(canManageTriage({ roles: ["viewer"] })).toBe(false);
    expect(canManageTriage({ roles: ["soc_analyst"] })).toBe(true);
    expect(canManageTriage({ roles: ["administrator"] })).toBe(true);
  });

  it("permits a dry run only after approval and appropriate authorization", () => {
    expect(canExecuteApprovedDryRun("pending_review", true)).toBe(false);
    expect(canExecuteApprovedDryRun("rejected", true)).toBe(false);
    expect(canExecuteApprovedDryRun("approved", false)).toBe(false);
    expect(canExecuteApprovedDryRun("approved", true)).toBe(true);
  });

  it("encodes incident navigation identifiers safely", () => {
    expect(incidentHref("incident/a b")).toBe("/incidents/incident%2Fa%20b");
  });
});
