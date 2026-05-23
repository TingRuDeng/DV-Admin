import type { PopoverProps } from "element-plus";

export type TableSelectRecord = Record<string, unknown>;
export type TableSelectFieldValue =
  | string
  | number
  | boolean
  | Date
  | TableSelectRecord
  | Array<string | number | boolean | Date | TableSelectRecord>
  | [Date, Date]
  | null
  | undefined;

export interface TableSelectQueryParams extends Record<string, TableSelectFieldValue> {
  pageNum: number;
  pageSize: number;
}

export interface TableSelectPageResult<TRecord extends TableSelectRecord = TableSelectRecord> {
  list: TRecord[];
  total: number;
}

export interface TableSelectOption {
  label: string;
  value: TableSelectFieldValue;
}

export interface TableSelectFormItem {
  type?: "input" | "select" | "tree-select" | "date-picker";
  label: string;
  prop: string;
  attrs?: TableSelectRecord;
  initialValue?: TableSelectFieldValue;
  options?: TableSelectOption[];
}

export interface TableSelectColumn extends TableSelectRecord {
  type?: "default" | "selection" | "index" | "expand";
  label?: string;
  prop?: string;
  width?: string | number;
  templet?: "custom";
  slotName?: string;
  reserveSelection?: boolean;
}

export interface TableSelectConfig<
  TQuery extends TableSelectQueryParams = TableSelectQueryParams,
  TRecord extends TableSelectRecord = TableSelectRecord,
> {
  width?: string;
  placeholder?: string;
  popover?: Partial<Omit<PopoverProps, "visible" | "v-model:visible">>;
  indexAction: (queryParams: TQuery) => Promise<TableSelectPageResult<TRecord>>;
  pk?: string;
  multiple?: boolean;
  formItems: TableSelectFormItem[];
  tableColumns: TableSelectColumn[];
}

export type IObject = TableSelectRecord;
export type ISelectConfig<
  TQuery extends TableSelectQueryParams = TableSelectQueryParams,
  TRecord extends TableSelectRecord = TableSelectRecord,
> = TableSelectConfig<TQuery, TRecord>;
