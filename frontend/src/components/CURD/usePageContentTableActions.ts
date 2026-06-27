import { ref } from "vue";
import type { IContentConfig, IObject, IOperateData } from "./types";

interface UsePageContentTableActionsOptions {
  contentConfig: IContentConfig;
  pk: string;
  handleRefresh: (isRestart?: boolean) => void;
  clearSelection: () => void;
  emitOperateClick: (data: IOperateData) => void;
}

export function usePageContentTableActions(options: UsePageContentTableActionsOptions) {
  const { contentConfig, pk, handleRefresh, clearSelection, emitOperateClick } = options;
  const selectionData = ref<IObject[]>([]);
  const removeIds = ref<(number | string)[]>([]);

  function handleSelectionChange(selection: IObject[]) {
    selectionData.value = selection;
    removeIds.value = selection.map((item) => toRowId(item[pk])).filter(isRowId);
  }

  function getSelectionData() {
    return selectionData.value;
  }

  function handleDelete(id?: number | string) {
    const ids = [id || removeIds.value].join(",");
    if (!ids) {
      ElMessage.warning("请勾选删除项");
      return;
    }

    ElMessageBox.confirm("确认删除?", "警告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(() => deleteRows(ids))
      .catch(() => {});
  }

  function handleOperate(data: IOperateData) {
    if (data.name === "delete" && contentConfig.deleteAction) {
      handleDelete(toRowId(data.row[pk]));
      return;
    }
    emitOperateClick(data);
  }

  function handleModify(field: string, value: boolean | string | number, row: IObject) {
    if (!contentConfig.modifyAction) {
      ElMessage.error("未配置modifyAction");
      return;
    }
    contentConfig.modifyAction({
      [pk]: row[pk],
      field,
      value,
    });
  }

  function deleteRows(ids: string) {
    if (!contentConfig.deleteAction) {
      ElMessage.error("未配置deleteAction");
      return;
    }

    contentConfig
      .deleteAction(ids)
      .then(() => {
        ElMessage.success("删除成功");
        removeIds.value = [];
        clearSelection();
        handleRefresh(true);
      })
      .catch(() => {});
  }

  return {
    selectionData,
    removeIds,
    getSelectionData,
    handleSelectionChange,
    handleDelete,
    handleOperate,
    handleModify,
  };
}

// 删除操作只接受字符串或数字主键，其他动态值不进入删除 ID 列表。
function toRowId(value: unknown) {
  return typeof value === "string" || typeof value === "number" ? value : undefined;
}

// 过滤掉无法安全作为删除主键的动态值。
function isRowId(value: string | number | undefined): value is string | number {
  return value !== undefined;
}
