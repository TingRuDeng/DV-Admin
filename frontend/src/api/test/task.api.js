import request from "@/utils/request";

const TASK_BASE_URL = "/api/test/tasks";

// 在TaskAPI对象中添加assignUsers方法
const TaskAPI = {
  /**
   * 获取任务分页列表
   * @param {Object} queryParams 查询参数
   * @returns {Promise} 任务分页列表
   */
  getPage(queryParams) {
    return request({
      url: `${TASK_BASE_URL}/`,
      method: "get",
      params: queryParams,
    });
  },

  /**
   * 获取任务表单详情
   * @param {string} taskId 任务ID
   * @returns {Promise} 任务表单详情
   */
  getFormData(taskId) {
    return request({
      url: `${TASK_BASE_URL}/${taskId}/`,
      method: "get",
    });
  },

  /**
   * 添加任务
   * @param {Object} data 任务表单数据
   * @returns {Promise} 添加结果
   */
  create(data) {
    return request({
      url: `${TASK_BASE_URL}/`,
      method: "post",
      data,
    });
  },

  /**
   * 修改任务
   * @param {string} id 任务ID
   * @param {Object} data 任务表单数据
   * @returns {Promise} 修改结果
   */
  update(id, data) {
    return request({
      url: `${TASK_BASE_URL}/${id}/`,
      method: "put",
      data,
    });
  },

  /**
   * 批量删除任务，多个以英文逗号(,)分割
   * @param {string} ids 任务ID字符串，多个以英文逗号(,)分割
   * @returns {Promise} 删除结果
   */
  deleteByIds(ids) {
    return request({
      url: `${TASK_BASE_URL}/${ids}/`,
      method: "delete",
    });
  },

  /**
   * 下载任务导入模板
   * @returns {Promise} 模板文件
   */
  downloadTemplate() {
    return request({
      url: `${TASK_BASE_URL}/template/`,
      method: "get",
      responseType: "blob",
    });
  },

  /**
   * 导出任务
   * @param {Object} queryParams 查询参数
   * @returns {Promise} 导出文件
   */
  export(queryParams) {
    return request({
      url: `${TASK_BASE_URL}/export/`,
      method: "get",
      params: queryParams,
      responseType: "blob",
    });
  },

  /**
   * 导入任务
   * @param {string} deptId 部门ID
   * @param {File} file 导入文件
   * @returns {Promise} 导入结果
   */
  import(deptId, file) {
    const formData = new FormData();
    formData.append("file", file);
    return request({
      url: `${TASK_BASE_URL}/import`,
      method: "post",
      params: { deptId },
      data: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  /**
   * 获取用户选项列表
   * @returns {Promise} 用户选项列表
   */
  getOptions() {
    return request({
      url: `${USER_BASE_URL}/options`,
      method: "get",
    });
  },

  /**
   * 分配任务给用户
   * @param {string} taskId 任务ID
   * @param {Array} userIds 用户ID数组
   * @returns {Promise} 分配结果
   */
  assignUsers(taskId, owners) {
    return request({
      url: `${TASK_BASE_URL}/${taskId}/`,
      method: "patch",
      data: { owners },
    });
  },
};

export default TaskAPI;
