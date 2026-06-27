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
        filters[key] = newFilters[key].join(col.filterJoin);
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
