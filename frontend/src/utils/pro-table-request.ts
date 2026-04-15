type ProTableParams = Record<string, unknown>;

export interface ProTableRequestResult<TItem> {
  list: TItem[];
  total: number;
}

function stripPaginationParams(params: ProTableParams): ProTableParams {
  const query = { ...params };
  delete query.pageNum;
  delete query.pageSize;
  return query;
}

export function createPageRequest<TQuery extends object, TItem>(
  fetcher: (query: TQuery) => Promise<PageResult<TItem[]>>
) {
  return (params: ProTableParams): Promise<ProTableRequestResult<TItem>> => {
    return fetcher(params as unknown as TQuery);
  };
}

export function createListRequest<TQuery extends object, TItem>(
  fetcher: (query: TQuery) => Promise<TItem[]>,
  options?: {
    stripPagination?: boolean;
  }
) {
  return async (params: ProTableParams): Promise<ProTableRequestResult<TItem>> => {
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
