export type NoticeOptionTagType = "success" | "warning" | "danger" | "primary" | "info";

export interface NoticeOption<T extends string | number> {
  value: T;
  label: string;
  tagType: NoticeOptionTagType;
}

export const NOTICE_TYPE_OPTIONS: readonly NoticeOption<number>[] = [
  { value: 1, label: "系统升级", tagType: "success" },
  { value: 2, label: "系统维护", tagType: "warning" },
  { value: 3, label: "安全警告", tagType: "danger" },
  { value: 4, label: "假期通知", tagType: "success" },
  { value: 5, label: "公司新闻", tagType: "primary" },
  { value: 99, label: "其他", tagType: "info" },
];

export const NOTICE_LEVEL_OPTIONS: readonly NoticeOption<string>[] = [
  { value: "L", label: "低", tagType: "info" },
  { value: "M", label: "中", tagType: "warning" },
  { value: "H", label: "高", tagType: "danger" },
];

export type NoticeOptionKind = "type" | "level";

export function getNoticeOption(kind: NoticeOptionKind, value: string | number | undefined) {
  const options = kind === "type" ? NOTICE_TYPE_OPTIONS : NOTICE_LEVEL_OPTIONS;
  return options.find((option) => String(option.value) === String(value));
}
