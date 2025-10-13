import request from "@/utils/request";

const CASE_BASE_URL = "/api/test/cases";

/**
 * 用例查询参数
 */
export interface CaseQuery {
  /** 搜索关键字 */
  search?: string;
  /** 状态 */
  status?: number;
  /** 项目ID */
  projectId?: string;
  /** 其他可选查询参数 */
  [key: string]: any;
}

/**
 * 用例表单数据
 */
export interface CaseForm {
  /** 用例ID */
  id?: string;
  /** 用例名称 */
  name?: string;
  /** 用例描述 */
  description?: string;
  /** 用例状态(1:启用；0:禁用) */
  status?: number;
  /** 项目ID */
  projectId?: string;
  /** 用例类型 */
  type?: string;
  /** 优先级 */
  priority?: number;
  /** 前置条件 */
  precondition?: string;
  /** 测试步骤 */
  steps?: string;
  /** 预期结果 */
  expectedResult?: string;
  /** 排序 */
  sort?: number;
  /** 其他用例字段 */
  [key: string]: any;
}

/**
 * 用例视图数据
 */
export interface CaseVO extends CaseForm {
  /** 创建时间 */
  createTime?: string;
  /** 修改时间 */
  updateTime?: string;
  /** 创建人 */
  createBy?: string;
  /** 修改人 */
  updateBy?: string;
  /** 项目名称 */
  projectName?: string;
  /** 其他展示字段 */
  [key: string]: any;
}

/**
 * 下拉选项类型
 */
export interface OptionType {
  value: string | number;
  label: string;
  [key: string]: any;
}

const CaseAPI = {
  /**
   * 获取用例列表
   * @param queryParams 查询参数（可选）
   * @returns {Promise} 用例表格数据
   */
  getList(queryParams?: CaseQuery) {
    return request<any, CaseVO[]>({
      url: `${CASE_BASE_URL}/`,
      method: "get",
      params: queryParams,
    });
  },

  /**
   * 获取用例下拉列表
   * @returns {Promise} 用例下拉列表数据
   */
  getOptions() {
    return request<any, OptionType[]>({
      url: `${CASE_BASE_URL}/options/`,
      method: "get",
    });
  },

  /**
   * 获取用例表单数据
   * @param id 用例ID
   * @returns {Promise} 用例表单数据
   */
  getFormData(id: string) {
    return request<any, CaseForm>({
      url: `${CASE_BASE_URL}/${id}/`,
      method: "get",
    });
  },

  /**
   * 新增用例
   * @param data 用例表单数据
   * @returns {Promise} 请求结果
   */
  create(data: CaseForm) {
    return request({
      url: `${CASE_BASE_URL}/`,
      method: "post",
      data,
    });
  },

  /**
   * 修改用例
   * @param id 用例ID
   * @param data 用例表单数据
   * @returns {Promise} 请求结果
   */
  update(id: string, data: CaseForm) {
    return request({
      url: `${CASE_BASE_URL}/${id}/`,
      method: "put",
      data,
    });
  },

  /**
   * 删除用例
   * @param ids 用例ID，多个以英文逗号(,)分隔
   * @returns {Promise} 请求结果
   */
  deleteByIds(ids: string) {
    return request({
      url: `${CASE_BASE_URL}/${ids}/`,
      method: "delete",
    });
  },
};

export default CaseAPI;
