import type { IContentConfig, IObject } from "./types";

type PageContentColumn = IContentConfig["cols"][number];

export function usePageContentFilters(
  cols: PageContentColumn[],
  emitFilterChange: (data: IObject) => void
) {
  let filterParams: IObject = {};

  function handleFilterChange(newFilters: IObject) {
    const filters: IObject = {};
    for (const key in newFilters) {
      const col = findFilterColumn(cols, key);
      if (col && col.filterJoin !== undefined) {
        filters[key] = joinFilterValue(newFilters[key], col.filterJoin);
      } else {
        filters[key] = newFilters[key];
      }
    }
    filterParams = { ...filterParams, ...filters };
    emitFilterChange(filterParams);
  }

  function getFilterParams() {
    return filterParams;
  }

  return {
    handleFilterChange,
    getFilterParams,
  };
}

function findFilterColumn(cols: PageContentColumn[], key: string) {
  return cols.find((col) => col.columnKey === key || col["column-key"] === key);
}

// 只有数组筛选值支持 filterJoin，其他动态值保持原样透传。
function joinFilterValue(value: unknown, join: string) {
  return Array.isArray(value) ? value.map(String).join(join) : value;
}
