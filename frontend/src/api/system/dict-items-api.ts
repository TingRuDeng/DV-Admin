import request from "@/utils/request";

const DICT_BASE_URL = "/api/system/dict-items";

const DictItemAPI = {
  /** 获取字典项分页列表 */
  getDictItemPage(queryParams: DictItemPageQuery) {
    return request<any, PageResult<DictItemPageVO[]>>({
      url: `${DICT_BASE_URL}/`,
      method: "get",
      params: queryParams,
    });
  },
  /** 新增字典项 */
  createDictItem(data: DictItemForm) {
    return request({ url: `${DICT_BASE_URL}/`, method: "post", data });
  },
  /** 获取字典项表单数据 */
  getDictItemFormData(id: number) {
    return request<any, DictItemForm>({
      url: `${DICT_BASE_URL}/${id}/`,
      method: "get",
    });
  },
  /** 修改字典项 */
  updateDictItem(id: string, data: DictItemForm) {
    return request({ url: `${DICT_BASE_URL}/${id}/`, method: "put", data });
  },
  /** 删除字典项 */
  deleteDictItems(ids: number[]) {
    return request({ url: `${DICT_BASE_URL}/`, method: "delete", data: { ids } });
  },
};

export default DictItemAPI;

export interface DictItemOption {
  /** 值 */
  id: number | string;
  /** 标签 */
  label: string;
  /** 标签类型 */
  tagType?: "" | "success" | "info" | "warning" | "danger";
  [key: string]: any;
}

export interface DictItemQuery {
  dict__dict_code: string;
}

export interface DictItemPageQuery extends PageQuery {
  /** 字典ID */
  dict?: number;
  /** 搜索关键字 */
  search?: string;
  /** 字典编码 */
  dictCode?: string;
}

export interface DictItemPageVO {
  /** 字典项ID */
  id: string;
  /** 字典编码 */
  dictCode: string;
  /** 字典项值 */
  value: string;
  /** 字典项标签 */
  label: string;
  /** 状态(1:启用;0:禁用) */
  status: number;
  /** 排序 */
  sort?: number;
}

export interface DictItemForm {
  /** 字典项ID(新增不填) */
  id?: string;
  /** 字典项ID(新增不填) */
  dict?: string;
  /** 字典编码 */
  dictCode?: string;
  /** 字典项值 */
  value?: string;
  /** 字典项标签 */
  label?: string;
  /** 状态(1:启用;0:禁用) */
  status?: number;
  /** 排序 */
  sort?: number;
  /** 标签类型 */
  tagType?: "success" | "warning" | "info" | "primary" | "danger" | "";
}
