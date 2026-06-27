import { describe, expect, it, vi } from "vitest";
import { usePageContentFilters } from "@/components/CURD/usePageContentFilters";
import type { IContentConfig, IObject } from "@/components/CURD/types";

type PageContentColumn = IContentConfig["cols"][number];

describe("usePageContentFilters", () => {
  it("保留普通筛选值并触发 filterChange", () => {
    const emitFilterChange = vi.fn();
    const filters = usePageContentFilters(
      [{ prop: "status", columnKey: "status" }] as PageContentColumn[],
      emitFilterChange
    );

    filters.handleFilterChange({ status: ["enabled"] });

    expect(filters.getFilterParams()).toEqual({ status: ["enabled"] });
    expect(emitFilterChange).toHaveBeenCalledWith({ status: ["enabled"] });
  });

  it("按列配置的 filterJoin 拼接筛选数组", () => {
    const emitFilterChange = vi.fn();
    const filters = usePageContentFilters(
      [{ prop: "role", columnKey: "role", filterJoin: "," }] as PageContentColumn[],
      emitFilterChange
    );

    filters.handleFilterChange({ role: ["admin", "visitor"] });

    expect(filters.getFilterParams()).toEqual({ role: "admin,visitor" });
  });

  it("兼容 Element Plus 的 column-key 字段", () => {
    const emitFilterChange = vi.fn();
    const filters = usePageContentFilters(
      [{ prop: "dept", "column-key": "deptFilter", filterJoin: "|" }] as PageContentColumn[],
      emitFilterChange
    );

    filters.handleFilterChange({ deptFilter: ["dev", "ops"] });

    expect(emitFilterChange).toHaveBeenCalledWith({ deptFilter: "dev|ops" });
  });

  it("多次筛选会增量合并既有筛选参数", () => {
    const emitted: IObject[] = [];
    const filters = usePageContentFilters(
      [
        { prop: "status", columnKey: "status" },
        { prop: "role", columnKey: "role", filterJoin: "," },
      ] as PageContentColumn[],
      (data) => emitted.push(data)
    );

    filters.handleFilterChange({ status: ["enabled"] });
    filters.handleFilterChange({ role: ["admin", "visitor"] });

    expect(filters.getFilterParams()).toEqual({
      status: ["enabled"],
      role: "admin,visitor",
    });
    expect(emitted).toEqual([
      { status: ["enabled"] },
      { status: ["enabled"], role: "admin,visitor" },
    ]);
  });
});
