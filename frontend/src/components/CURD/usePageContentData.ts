import { reactive, ref } from "vue";
import type { IContentConfig, IObject } from "./types";

const defaultPagination = {
  background: true,
  layout: "total, sizes, prev, pager, next, jumper",
  pageSize: 20,
  pageSizes: [10, 20, 30, 50],
  total: 0,
  currentPage: 1,
};

export function usePageContentData(contentConfig: IContentConfig) {
  const loading = ref(false);
  const pageData = ref<IObject[]>([]);
  const showPagination = contentConfig.pagination !== false;
  const pagination = reactive(
    typeof contentConfig.pagination === "object"
      ? { ...defaultPagination, ...contentConfig.pagination }
      : { ...defaultPagination }
  );
  const request = contentConfig.request ?? {
    pageName: "pageNum",
    limitName: "pageSize",
  };
  let lastFormData: IObject = {};

  async function fetchPageData(formData: IObject = {}, isRestart = false) {
    loading.value = true;
    lastFormData = formData;
    if (isRestart) {
      pagination.currentPage = 1;
    }

    try {
      const data = await contentConfig.indexAction(buildQueryParams(formData));
      applyPageData(data);
    } finally {
      loading.value = false;
    }
  }

  function handleRefresh(isRestart = false) {
    fetchPageData(lastFormData, isRestart);
  }

  function handleSizeChange(value: number) {
    pagination.pageSize = value;
    handleRefresh();
  }

  function handleCurrentChange(value: number) {
    pagination.currentPage = value;
    handleRefresh();
  }

  function getLastFormData() {
    return lastFormData;
  }

  function buildQueryParams(formData: IObject) {
    if (!showPagination) {
      return formData;
    }

    return {
      [request.pageName]: pagination.currentPage,
      [request.limitName]: pagination.pageSize,
      ...formData,
    };
  }

  function applyPageData(data: any) {
    if (!showPagination) {
      pageData.value = data;
      return;
    }

    const parsedData = contentConfig.parseData ? contentConfig.parseData(data) : data;
    pagination.total = parsedData.total;
    pageData.value = parsedData.list;
  }

  return {
    loading,
    pageData,
    showPagination,
    pagination,
    fetchPageData,
    getLastFormData,
    handleRefresh,
    handleSizeChange,
    handleCurrentChange,
  };
}
