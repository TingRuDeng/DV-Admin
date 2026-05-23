import { beforeEach, describe, expect, it, vi } from "vitest";
import { hasPerm } from "@/utils/auth";

const userInfo = vi.hoisted(() => ({}));

vi.mock("@/store/modules/user-store", () => ({
  useUserStoreHook: () => ({
    userInfo,
  }),
}));

vi.mock("@/router", () => ({
  default: {
    currentRoute: { value: { fullPath: "/" } },
    push: vi.fn(),
  },
}));

describe("hasPerm", () => {
  beforeEach(() => {
    Object.keys(userInfo).forEach((key) => {
      delete (userInfo as Record<string, unknown>)[key];
    });
  });

  it("returns false instead of throwing when user info is empty", () => {
    expect(() => hasPerm("system:user:add")).not.toThrow();
    expect(hasPerm("system:user:add")).toBe(false);
  });
});
