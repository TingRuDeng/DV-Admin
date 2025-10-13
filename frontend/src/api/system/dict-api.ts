import request from "@/utils/request";

const DICT_BASE_URL = "/api/system/dicts";

const DictAPI = {
  /** 字典分页列表 */
  getPage(queryParams?: DictPageQuery) {
    return request<any, PageResult<DictPageVO[]>>({
      url: `${DICT_BASE_URL}/`,
      method: "get",
      params: queryParams,
    });
  },
  /** 字典列表 */
  getList() {
    return request<any, OptionType[]>({ url: `${DICT_BASE_URL}`, method: "get" });
  },
  /** 字典表单数据 */
  getFormData(id: string) {
    return request<any, DictForm>({ url: `${DICT_BASE_URL}/${id}/`, method: "get" });
  },
  /** 新增字典 */
  create(data: DictForm) {
    return request({ url: `${DICT_BASE_URL}/`, method: "post", data });
  },
  /** 修改字典 */
  update(id: string, data: DictForm) {
    return request({ url: `${DICT_BASE_URL}/${id}/`, method: "put", data });
  },
  /** 删除字典 */
  deleteByIds(ids: number[]) {
    return request({ url: `${DICT_BASE_URL}/`, method: "delete", data: { ids } });
  },
};

export default DictAPI;

export interface DictPageQuery extends PageQuery {
  /** 搜索关键字 */
  search?: string;
  /** 状态(1:启用;0:禁用) */
  status?: number;
}
export interface DictPageVO {
  /** 字典ID */
  id: string;
  /** 字典名称 */
  name: string;
  /** 字典编码 */
  dictCode: string;
  /** 状态(1:启用;0:禁用) */
  status: number;
}
export interface DictForm {
  /** 字典ID(新增不填) */
  id?: string;
  /** 字典名称 */
  name?: string;
  /** 字典编码 */
  dictCode?: string;
  /** 状态(1:启用;0:禁用) */
  status?: number;
  /** 备注 */
  remark?: string;
}

// export interface DictItemOption {
//   /** 值 */
//   value: number | string;
//   /** 标签 */
//   label: string;
//   /** 标签类型 */
//   tagType?: "" | "success" | "info" | "warning" | "danger";
//   [key: string]: any;
// }
