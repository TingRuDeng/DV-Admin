import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import DictItemAPI from "@/api/system/dict-items-api";
import { useDictStore } from "@/store/modules/dict-store";

vi.mock("@/api/system/dict-items-api", () => ({
  default: {
    getDictItems: vi.fn(),
  },
}));

describe("useDictStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  it("clears request queue after a failed dict request", async () => {
    vi.mocked(DictItemAPI.getDictItems).mockRejectedValueOnce(new Error("network error"));
    const dictStore = useDictStore();

    await expect(dictStore.loadDictItems("gender")).rejects.toThrow("network error");

    vi.mocked(DictItemAPI.getDictItems).mockResolvedValueOnce([]);
    await expect(dictStore.loadDictItems("gender")).resolves.toBeUndefined();
    expect(DictItemAPI.getDictItems).toHaveBeenCalledTimes(2);
  });
});
