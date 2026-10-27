import { describe, expect, it } from "vitest";
import { canManageDataSources, healthStateLabel, responseStatusLabel } from "./administration";

describe("administration workspace helpers", () => {
  it("keeps viewer data-source controls read only", () => {
    expect(canManageDataSources({ roles: ["viewer"] })).toBe(false);
    expect(canManageDataSources({ roles: ["administrator"] })).toBe(true);
  });

  it("does not upgrade unreported health to healthy", () => {
    expect(healthStateLabel()).toBe("Not reported");
    expect(healthStateLabel("degraded")).toBe("Degraded");
    expect(healthStateLabel("error")).toBe("Unavailable");
  });

  it("renders durable response lifecycle states readably", () => {
    expect(responseStatusLabel("pending_review")).toBe("Pending Review");
    expect(responseStatusLabel("dry_run_completed")).toBe("Dry Run Completed");
  });
});
