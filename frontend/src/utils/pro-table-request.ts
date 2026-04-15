import type { ProTableQuery, ProTableRequestResult } from "@/components/ProTable/types";

function stripPaginationParams(params: Record<string, unknown>): ProTableQuery {
  const query = { ...params };
  Reflect.deleteProperty(query, "pageNum");
  Reflect.deleteProperty(query, "pageSize");
  return query;
}

export function createPageRequest<TQuery extends object, TItem>(
  fetcher: (query: TQuery) => Promise<PageResult<TItem[]>>
) {
  return (params: Record<string, unknown>): Promise<ProTableRequestResult<TItem>> => {
    return fetcher(params as unknown as TQuery);
  };
}

export function createListRequest<TQuery extends object, TItem>(
  fetcher: (query: TQuery) => Promise<TItem[]>,
  options?: {
    stripPagination?: boolean;
  }
) {
  return async (params: Record<string, unknown>): Promise<ProTableRequestResult<TItem>> => {
    const query = (options?.stripPagination
      ? stripPaginationParams(params)
      : params) as unknown as TQuery;
    const list = await fetcher(query);
    return {
      list,
      total: list.length,
    };
  };
}
