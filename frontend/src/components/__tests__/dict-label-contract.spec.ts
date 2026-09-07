import { createPinia, setActivePinia } from "pinia";
import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import DictLabel from "@/components/Dict/DictLabel.vue";
import DictItemAPI from "@/api/system/dict-items-api";
import { useDictStore } from "@/store/modules/dict-store";
import { STORAGE_KEYS } from "@/constants";
import request from "@/utils/request";

vi.mock("@/utils/request", () => ({ default: vi.fn() }));

const first = { value: "0", label: "未读", tagType: "info" };
const second = { value: "1", label: "已读", tagType: "primary" };

describe("dictionary option contract", () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
    vi.mocked(request).mockReset();
  });

  it("loads every page with the shared dictCode filter", async () => {
    vi.mocked(request)
      .mockResolvedValueOnce({ list: [first], total: 2 })
      .mockResolvedValueOnce({ list: [second], total: 2 });

    expect(await DictItemAPI.getDictItems({ dictCode: "read_status" })).toEqual([first, second]);
    expect(request).toHaveBeenNthCalledWith(1, {
      url: "/api/system/dict-items/",
      method: "get",
      params: { dictCode: "read_status", pageNum: 1, pageSize: 100 },
    });
    expect(request).toHaveBeenNthCalledWith(2, {
      url: "/api/system/dict-items/",
      method: "get",
      params: { dictCode: "read_status", pageNum: 2, pageSize: 100 },
    });
  });

  it.each([{ old: { list: [first], total: 1 } }, { old: [first] }])(
    "ignores legacy unfiltered cache $old",
    async ({ old }) => {
      localStorage.setItem("vea:system:dict_cache", JSON.stringify({ read_status: old }));
      vi.mocked(request).mockResolvedValue({ list: [second], total: 1 });
      const store = useDictStore();

      await store.loadDictItems("read_status");
      expect(store.getDictItems("read_status")).toEqual([second]);
      expect(request).toHaveBeenCalledOnce();
    }
  );

  it("refetches malformed cached entries and coalesces concurrent readers", async () => {
    localStorage.setItem(STORAGE_KEYS.DICT_CACHE, JSON.stringify({ read_status: { list: [] } }));
    vi.mocked(request).mockResolvedValue({ list: [second], total: 1 });
    const store = useDictStore();

    expect(store.getDictItems("read_status")).toEqual([]);
    await Promise.all([store.loadDictItems("read_status"), store.loadDictItems("read_status")]);
    expect(store.getDictItems("read_status")).toEqual([second]);
    expect(request).toHaveBeenCalledOnce();
  });

  it("does not cache a partial list on failure and allows retry", async () => {
    vi.mocked(request)
      .mockResolvedValueOnce({ list: [first], total: 2 })
      .mockRejectedValueOnce(new Error("offline"));
    const store = useDictStore();
    await expect(store.loadDictItems("read_status")).rejects.toThrow("offline");
    expect(store.getDictItems("read_status")).toEqual([]);

    vi.mocked(request).mockResolvedValueOnce({ list: [second], total: 1 });
    await store.loadDictItems("read_status");
    expect(store.getDictItems("read_status")).toEqual([second]);
  });

  it.each([{ data: [] }, { data: { list: [], total: 2 } }, { data: { list: [], total: -1 } }])(
    "rejects an invalid or incomplete page instead of caching success: $data",
    async ({ data }) => {
      vi.mocked(request).mockResolvedValue(data);
      await expect(DictItemAPI.getDictItems({ dictCode: "read_status" })).rejects.toThrow();
    }
  );

  it("renders the selected label and tag from a paginated response without Vue errors", async () => {
    vi.mocked(request).mockResolvedValue({ list: [second], total: 1 });
    const errorHandler = vi.fn();
    const wrapper = mount(DictLabel, {
      props: { code: "read_status", modelValue: 1 },
      global: {
        plugins: [createPinia()],
        config: { errorHandler },
        stubs: { ElTag: { props: ["type"], template: '<span :data-type="type"><slot /></span>' } },
      },
    });
    await flushPromises();
    expect(errorHandler).not.toHaveBeenCalled();
    expect(wrapper.text()).toBe("已读");
    expect(wrapper.get('[data-type="primary"]').text()).toBe("已读");
    wrapper.unmount();
  });
});
