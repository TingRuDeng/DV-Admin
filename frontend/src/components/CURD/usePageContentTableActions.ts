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
    removeIds.value = selection.map((item) => item[pk]);
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
      handleDelete(data.row[pk]);
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
