import { hasPerm } from "@/utils/auth";
import type { ButtonProps } from "element-plus";
import { computed, type CSSProperties } from "vue";
import type { IContentConfig, IObject, IToolsButton } from "./types";

interface DefaultButtonConfig {
  text: string;
  attrs: Partial<ButtonProps> & { style?: CSSProperties };
  perm: string;
}

export interface PageContentToolbarButton {
  name: string;
  text?: string;
  perm?: string | null;
  attrs?: Partial<ButtonProps> & { style?: CSSProperties };
  render?: (row: IObject) => boolean;
}

const DEFAULT_BUTTON_CONFIG: Record<string, DefaultButtonConfig> = {
  add: { text: "新增", attrs: { icon: "plus", type: "success" }, perm: "add" },
  delete: { text: "删除", attrs: { icon: "delete", type: "danger" }, perm: "delete" },
  import: { text: "导入", attrs: { icon: "upload", type: "" }, perm: "import" },
  export: { text: "导出", attrs: { icon: "download", type: "" }, perm: "export" },
  refresh: { text: "刷新", attrs: { icon: "refresh", type: "" }, perm: "*:*:*" },
  filter: { text: "筛选列", attrs: { icon: "operation", type: "" }, perm: "*:*:*" },
  search: { text: "搜索", attrs: { icon: "search", type: "" }, perm: "search" },
  imports: { text: "批量导入", attrs: { icon: "upload", type: "" }, perm: "imports" },
  exports: { text: "批量导出", attrs: { icon: "download", type: "" }, perm: "exports" },
  view: { text: "查看", attrs: { icon: "view", type: "primary" }, perm: "view" },
  edit: { text: "编辑", attrs: { icon: "edit", type: "primary" }, perm: "edit" },
};

type ToolbarAttrs = Partial<ButtonProps> & { style?: CSSProperties };

export function usePageContentToolbarConfig(contentConfig: IContentConfig) {
  const authPrefix = computed(() => contentConfig.permPrefix);

  // 按权限前缀把短权限动作转换为完整权限标识。
  function getButtonPerm(action: string): string | null {
    if (action.includes(":")) {
      return action;
    }
    return authPrefix.value ? `${authPrefix.value}:${action}` : null;
  }

  // 没有权限前缀时保持历史默认行为：按钮可见且可用。
  function hasButtonPerm(action: string): boolean {
    const perm = getButtonPerm(action);
    if (!perm) return true;
    return hasPerm(perm);
  }

  // 同时兼容默认按钮名和调用方传入的自定义按钮配置。
  function createToolbar(
    toolbar: Array<string | IToolsButton>,
    attr: ToolbarAttrs = {}
  ): PageContentToolbarButton[] {
    return toolbar.map((item) => {
      const isString = typeof item === "string";
      const defaultConfig = isString ? DEFAULT_BUTTON_CONFIG[item] : undefined;
      return {
        name: isString ? item : item?.name || "",
        text: isString ? defaultConfig!.text : item?.text,
        attrs: {
          ...attr,
          ...(isString ? defaultConfig!.attrs : item?.attrs),
        },
        render: isString ? undefined : (item?.render ?? undefined),
        perm: isString
          ? getButtonPerm(defaultConfig!.perm)
          : item?.perm
            ? getButtonPerm(item.perm as string)
            : "*:*:*",
      };
    });
  }

  const toolbarLeftBtn = computed(() => {
    if (!contentConfig.toolbar || contentConfig.toolbar.length === 0) return [];
    return createToolbar(contentConfig.toolbar, {});
  });

  const toolbarRightBtn = computed(() => {
    if (!contentConfig.defaultToolbar || contentConfig.defaultToolbar.length === 0) return [];
    return createToolbar(contentConfig.defaultToolbar, { circle: true });
  });

  const tableToolbarBtn = computed(() => {
    const tableToolbar = contentConfig.cols[contentConfig.cols.length - 1].operat ?? [
      "edit",
      "delete",
    ];
    return createToolbar(tableToolbar, { link: true, size: "small" });
  });

  return {
    toolbarLeftBtn,
    toolbarRightBtn,
    tableToolbarBtn,
    hasButtonPerm,
  };
}
