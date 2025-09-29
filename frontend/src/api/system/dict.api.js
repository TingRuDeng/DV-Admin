import request from "@/utils/request";

const DICT_BASE_URL = "/system/dicts";
const DICT_ITEM_BASE_URL = "/system/dict-items";

const DictAPI = {
  //---------------------------------------------------
  // 字典相关接口
  //---------------------------------------------------

  /**
   * 字典分页列表
   * @param {Object} queryParams 查询参数
   * @returns {Promise} 字典分页结果
   */
  getPage(queryParams) {
    return request({
      url: `${DICT_BASE_URL}/`,
      method: "get",
      params: queryParams,
    });
  },

  /**
   * 字典列表
   * @returns {Promise} 字典列表
   */
  getList() {
    return request({
      url: `${DICT_BASE_URL}/`,
      method: "get",
    });
  },

  /**
   * 字典表单数据
   * @param {string} id 字典ID
   * @returns {Promise} 字典表单数据
   */
  getFormData(id) {
    return request({
      url: `${DICT_BASE_URL}/${id}/`,
      method: "get",
    });
  },

  /**
   * 新增字典
   * @param {Object} data 字典表单数据
   * @returns {Promise} 添加结果
   */
  create(data) {
    return request({
      url: `${DICT_BASE_URL}/`,
      method: "post",
      data: data,
    });
  },

  /**
   * 修改字典
   * @param {string} id 字典ID
   * @param {Object} data 字典表单数据
   * @returns {Promise} 修改结果
   */
  update(id, data) {
    return request({
      url: `${DICT_BASE_URL}/${id}/`,
      method: "put",
      data: data,
    });
  },

  /**
   * 删除字典
   * @param {string} ids 字典ID，多个以英文逗号(,)分隔
   * @returns {Promise} 删除结果
   */
  deleteByIds(ids) {
    return request({
      url: `${DICT_BASE_URL}/${ids}/`,
      method: "delete",
    });
  },

  //---------------------------------------------------
  // 字典项相关接口
  //---------------------------------------------------

  /**
   * 获取字典项列表
   * @returns {Promise} 字典项列表
   */
  // getDictItems() {
  //   return request({
  //     url: `${DICT_ITEM_BASE_URL}/`,
  //     method: "get",
  //   });
  // },
};

export default DictAPI;
