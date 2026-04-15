export type ProTableRow = unknown;

export type ProTableQuery = object;

export type ProTableRequestParams<TQuery extends ProTableQuery = ProTableQuery> = TQuery &
  PageQuery;

export interface ProTableRequestResult<TRow = ProTableRow> {
  list: TRow[];
  total: number;
}

export type ProTableRequest<TRow = ProTableRow, TQuery extends ProTableQuery = ProTableQuery> = (
  params: ProTableRequestParams<TQuery>
) => Promise<ProTableRequestResult<TRow>>;

export interface ProTablePaginationPayload {
  page: number;
  limit: number;
}

export interface ProTableExpose {
  reload: (resetPage?: boolean) => Promise<void>;
}
