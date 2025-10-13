import request from "@/utils/request";

const PROJECT_BASE_URL = "/api/test/projects";

/**
 * 项目查询参数
 */
export interface ProjectQuery {
  /** 搜索关键字 */
  search?: string;
  /** 状态 */
  status?: number;
  /** 其他可选查询参数 */
  [key: string]: any;
}

/**
 * 项目表单数据
 */
export interface ProjectForm {
  /** 项目ID */
  id?: string;
  /** 项目名称 */
  name?: string;
  /** 项目描述 */
  description?: string;
  /** 项目状态(1:启用；0:禁用) */
  status?: number;
  /** 排序 */
  sort?: number;
  /** 父项目ID */
  parentId?: string;
  /** 其他项目字段 */
  [key: string]: any;
}

/**
 * 项目视图数据
 */
export interface ProjectVO extends ProjectForm {
  /** 子项目列表 */
  children?: ProjectVO[];
  /** 创建时间 */
  createTime?: string;
  /** 修改时间 */
  updateTime?: string;
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

const ProjectApi = {
  /**
   * 获取项目列表
   * @param queryParams 查询参数（可选）
   * @returns {Promise} 项目树形表格数据
   */
  getList(queryParams?: ProjectQuery) {
    return request<any, ProjectVO[]>({
      url: `${PROJECT_BASE_URL}/`,
      method: "get",
      params: queryParams,
    });
  },

  /**
   * 获取项目下拉列表
   * @returns {Promise} 项目下拉列表数据
   */
  getOptions() {
    return request<any, OptionType[]>({
      url: `${PROJECT_BASE_URL}/`,
      method: "get",
    });
  },

  /**
   * 获取项目表单数据
   * @param id 项目ID
   * @returns {Promise} 项目表单数据
   */
  getFormData(id: string) {
    return request<any, ProjectForm>({
      url: `${PROJECT_BASE_URL}/${id}/`,
      method: "get",
    });
  },

  /**
   * 新增项目
   * @param data 项目表单数据
   * @returns {Promise} 请求结果
   */
  create(data: ProjectForm) {
    return request({
      url: `${PROJECT_BASE_URL}/`,
      method: "post",
      data,
    });
  },

  /**
   * 修改项目
   * @param id 项目ID
   * @param data 项目表单数据
   * @returns {Promise} 请求结果
   */
  update(id: string, data: ProjectForm) {
    return request({
      url: `${PROJECT_BASE_URL}/${id}/`,
      method: "put",
      data,
    });
  },

  /**
   * 删除项目
   * @param ids 项目ID，多个以英文逗号(,)分隔
   * @returns {Promise} 请求结果
   */
  deleteByIds(ids: string) {
    return request({
      url: `${PROJECT_BASE_URL}/${ids}/`,
      method: "delete",
    });
  },
};

export default ProjectApi;
