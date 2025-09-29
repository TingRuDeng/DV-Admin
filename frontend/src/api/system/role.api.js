import request from "@/utils/request";

const ROLE_BASE_URL = "/system/roles";

const RoleAPI = {
  /**
   * 获取角色分页数据
   * @param {Object} queryParams 查询参数
   * @returns {Promise} 角色分页数据
   */
  getPage(queryParams) {
    return request({
      url: `${ROLE_BASE_URL}/`,
      method: "get",
      params: queryParams,
    });
  },

  /**
   * 获取角色下拉数据源
   * @returns {Promise} 角色选项列表
   */
  getOptions() {
    return request({
      url: `${ROLE_BASE_URL}/options/`,
      method: "get",
    });
  },

  /**
   * 获取角色的菜单ID集合
   * @param {string} roleId 角色ID
   * @returns {Promise} 角色的菜单ID集合
   */
  getRoleMenuIds(roleId) {
    return request({
      url: `${ROLE_BASE_URL}/${roleId}/menuIds/`,
      method: "get",
    });
  },

  /**
   * 分配菜单权限
   * @param {string} roleId 角色ID
   * @param {Array} data 菜单ID集合
   * @returns {Promise} 分配结果
   */
  updateRoleMenus(roleId, data) {
    return request({
      url: `${ROLE_BASE_URL}/${roleId}/`,
      method: "patch",
      data: { permissions: data },
    });
  },

  /**
   * 获取角色表单数据
   * @param {string} id 角色ID
   * @returns {Promise} 角色表单数据
   */
  getFormData(id) {
    return request({
      url: `${ROLE_BASE_URL}/${id}/`,
      method: "get",
    });
  },

  /**
   * 添加角色
   * @param {Object} data 角色表单数据
   * @returns {Promise} 添加结果
   */
  create(data) {
    return request({
      url: `${ROLE_BASE_URL}/`,
      method: "post",
      data: data,
    });
  },

  /**
   * 更新角色
   * @param {string} id 角色ID
   * @param {Object} data 角色表单数据
   * @returns {Promise} 更新结果
   */
  update(id, data) {
    return request({
      url: `${ROLE_BASE_URL}/${id}/`,
      method: "put",
      data: data,
    });
  },

  /**
   * 删除角色
   * @param {string} id 角色ID
   * @returns {Promise} 删除结果
   */
  delete(id) {
    return request({
      url: `${ROLE_BASE_URL}/${id}/`,
      method: "delete",
    });
  },

  /**
   * 批量删除角色，多个以英文逗号(,)分割
   * @param {string} ids 角色ID字符串，多个以英文逗号(,)分割
   * @returns {Promise} 删除结果
   */
  deleteByIds(ids) {
    return request({
      url: `${ROLE_BASE_URL}/`,
      method: "delete",
      data: { ids: ids },
    });
  },
};

export default RoleAPI;
