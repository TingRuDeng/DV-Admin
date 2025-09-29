import request from "@/utils/request";

const DICT_BASE_URL = "/system/dict-items";

const DictItemAPI = {
  /**
   * 获取字典分页列表
   * @param {Object} queryParams 查询参数
   * @returns {Promise} 字典分页结果
   */
  getDictItems(queryParams) {
    return request({
      url: `${DICT_BASE_URL}/`,
      method: "get",
      params: queryParams,
    });
  },

  // /**
  //  * 获取字典项列表
  //  * @param {string} dictCode 字典编码
  //  * @returns {Promise} 字典项列表
  //  */
  // getDictItems(dictCode) {
  //   return request({
  //     url: `${DICT_BASE_URL}/${dictCode}/items/`,
  //     method: "get",
  //   });
  // },

  /**
   * 新增字典项
   * @param {Object} data 字典项表单数据
   * @returns {Promise} 添加结果
   */
  createDictItem(data) {
    return request({
      url: `${DICT_BASE_URL}/`,
      method: "post",
      data: data,
    });
  },

  /**
   * 获取字典项表单数据
   * @param {string} id 字典项ID
   * @returns {Promise} 字典项表单数据
   */
  getDictItemFormData(id) {
    return request({
      url: `${DICT_BASE_URL}/${id}/`,
      method: "get",
    });
  },

  /**
   * 修改字典项
   * @param {string} id 字典项ID
   * @param {Object} data 字典项表单数据
   * @returns {Promise} 修改结果
   */
  updateDictItem(data) {
    return request({
      url: `${DICT_BASE_URL}/${data.id}/`,
      method: "put",
      data: data,
    });
  },

  /**
   * 删除字典项
   * @param {string} ids 字典项ID，多个以英文逗号(,)分隔
   * @returns {Promise} 删除结果
   */
  deleteDictItems(ids) {
    return request({
      url: `${DICT_BASE_URL}/${ids}/`,
      method: "delete",
    });
  },
};

export default DictItemAPI;
