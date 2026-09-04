import { describe, expect, it } from "vitest";

import { runExclusive } from "@/utils/exclusive-action";

describe("runExclusive", () => {
  it("does not start a second action while the first action is pending", async () => {
    const state = { value: false };
    let resolveFirst!: (value: string) => void;
    let started = 0;
    const first = new Promise<string>((resolve) => {
      resolveFirst = resolve;
    });

    const firstRun = runExclusive(state, async () => {
      started += 1;
      return first;
    });
    const secondRun = await runExclusive(state, async () => {
      started += 1;
      return "second";
    });

    expect(secondRun).toBeUndefined();
    expect(started).toBe(1);
    expect(state.value).toBe(true);

    resolveFirst("first");
    await expect(firstRun).resolves.toBe("first");
    expect(state.value).toBe(false);
  });

  it("releases the guard when the action rejects", async () => {
    const state = { value: false };

    await expect(
      runExclusive(state, async () => {
        throw new Error("failed");
      })
    ).rejects.toThrow("failed");

    expect(state.value).toBe(false);
    await expect(runExclusive(state, async () => "retry")).resolves.toBe("retry");
  });
});
