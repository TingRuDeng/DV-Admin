import request from "@/utils/request";

const DEVICE_BASE_URL = "/api/test/devices";

const DeviceAPI = {
  /**
   * 获取设备列表
   * @param {Object} queryParams 查询参数（可选）
   * @returns {Promise} 设备树形表格数据
   */
  getList(queryParams) {
    return request({
      url: `${DEVICE_BASE_URL}/`,
      method: "get",
      params: queryParams,
    });
  },

  /**
   * 获取设备下拉列表
   * @returns {Promise} 设备下拉列表数据
   */
  getOptions() {
    return request({
      url: `${DEVICE_BASE_URL}/`,
      method: "get",
    });
  },

  /**
   * 获取设备表单数据
   * @param {string} id 设备ID
   * @returns {Promise} 设备表单数据
   */
  getFormData(id) {
    return request({
      url: `${DEVICE_BASE_URL}/${id}/`,
      method: "get",
    });
  },

  /**
   * 新增设备
   * @param {Object} data 设备表单数据
   * @returns {Promise} 请求结果
   */
  create(data) {
    return request({
      url: `${DEVICE_BASE_URL}/`,
      method: "post",
      data,
    });
  },

  /**
   * 修改设备
   * @param {string} id 设备ID
   * @param {Object} data 设备表单数据
   * @returns {Promise} 请求结果
   */
  update(id, data) {
    return request({
      url: `${DEVICE_BASE_URL}/${id}/`,
      method: "put",
      data,
    });
  },

  /**
   * 删除设备
   * @param {string} ids 设备ID，多个以英文逗号(,)分隔
   * @returns {Promise} 请求结果
   */
  deleteByIds(ids) {
    return request({
      url: `${DEVICE_BASE_URL}/${ids}/`,
      method: "delete",
    });
  },
};

export default DeviceAPI;
