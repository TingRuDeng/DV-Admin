import { describe, expect, it, vi } from "vitest";
import { usePageContentData } from "@/components/CURD/usePageContentData";
import type { IContentConfig } from "@/components/CURD/types";

function createContentConfig(overrides: Partial<IContentConfig> = {}): IContentConfig {
  return {
    cols: [],
    indexAction: vi.fn().mockResolvedValue({ list: [{ id: 1 }], total: 1 }),
    ...overrides,
  };
}

describe("usePageContentData", () => {
  it("分页模式按当前分页配置拼装请求参数并写入列表数据", async () => {
    const indexAction = vi.fn().mockResolvedValue({ list: [{ id: 1 }], total: 9 });
    const page = usePageContentData(createContentConfig({ indexAction }));

    await page.fetchPageData({ keyword: "admin" });

    expect(indexAction).toHaveBeenCalledWith({
      pageNum: 1,
      pageSize: 20,
      keyword: "admin",
    });
    expect(page.pageData.value).toEqual([{ id: 1 }]);
    expect(page.pagination.total).toBe(9);
    expect(page.loading.value).toBe(false);
  });

  it("非分页模式直接传递查询参数并使用响应作为列表数据", async () => {
    const indexAction = vi.fn().mockResolvedValue([{ id: 2 }]);
    const page = usePageContentData(
      createContentConfig({
        pagination: false,
        indexAction,
      })
    );

    await page.fetchPageData({ status: "enabled" });

    expect(indexAction).toHaveBeenCalledWith({ status: "enabled" });
    expect(page.pageData.value).toEqual([{ id: 2 }]);
  });

  it("分页模式支持自定义请求字段和响应解析", async () => {
    const indexAction = vi.fn().mockResolvedValue({ rows: [{ id: 3 }], count: 11 });
    const page = usePageContentData(
      createContentConfig({
        indexAction,
        request: { pageName: "page", limitName: "limit" },
        parseData: (data) => ({ list: data.rows, total: data.count }),
      })
    );

    await page.fetchPageData({ deptId: 1 });

    expect(indexAction).toHaveBeenCalledWith({ page: 1, limit: 20, deptId: 1 });
    expect(page.pageData.value).toEqual([{ id: 3 }]);
    expect(page.pagination.total).toBe(11);
  });

  it("刷新时可复用上一次查询条件并重置页码", async () => {
    const indexAction = vi.fn().mockResolvedValue({ list: [], total: 0 });
    const page = usePageContentData(createContentConfig({ indexAction }));

    page.pagination.currentPage = 4;
    await page.fetchPageData({ keyword: "visitor" });
    await page.fetchPageData(page.getLastFormData(), true);

    expect(indexAction).toHaveBeenLastCalledWith({
      pageNum: 1,
      pageSize: 20,
      keyword: "visitor",
    });
    expect(page.pagination.currentPage).toBe(1);
  });

  it("分页切换会更新分页状态并重新请求当前查询条件", async () => {
    const indexAction = vi.fn().mockResolvedValue({ list: [], total: 0 });
    const page = usePageContentData(createContentConfig({ indexAction }));

    await page.fetchPageData({ keyword: "admin" });
    page.handleSizeChange(50);
    page.handleCurrentChange(2);
    await vi.waitFor(() => expect(indexAction).toHaveBeenCalledTimes(3));

    expect(indexAction).toHaveBeenNthCalledWith(2, {
      pageNum: 1,
      pageSize: 50,
      keyword: "admin",
    });
    expect(indexAction).toHaveBeenNthCalledWith(3, {
      pageNum: 2,
      pageSize: 50,
      keyword: "admin",
    });
  });
});
