import request from "@/utils/request";

const INFO_BASE_URL = "/information";

const InformationAPI = {
  /**
   * 获取个人中心用户信息
   * @returns {Promise} 用户信息
   */
  getProfile() {
    return request({
      url: `${INFO_BASE_URL}/profile`,
      method: "get",
    });
  },

  /**
   * 修改个人中心用户信息
   * @param {Object} data 用户信息
   * @returns {Promise} 修改结果
   */
  updateProfile(data) {
    return request({
      url: `${INFO_BASE_URL}/change-information/`,
      method: "put",
      data: data,
    });
  },

  /**
   * 修改个人中心用户密码
   * @param {Object} data 密码信息
   * @returns {Promise} 修改结果
   */
  updatePassword(data) {
    return request({
      url: `${INFO_BASE_URL}/change-password/`,
      method: "put",
      data: data,
    });
  },

  /**
   * 修改个人头像
   * @param {Object} file 头像信息
   * @returns {Promise} 修改结果
   */
  // updateAvatar(data) {
  //   return request({
  //     url: `${INFO_BASE_URL}/change-avatar/`,
  //     method: "put",
  //     data: data,
  //   });
  // },
  // 修改updateAvatar方法，移除重复的FormData创建并简化实现
  updateAvatar(file) {
    // 如果传入的已经是FormData对象，直接使用
    if (file instanceof FormData) {
      return request({
        url: `${INFO_BASE_URL}/change-avatar/`,
        method: "post",
        data: file,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
    }
    // // 如果传入的是文件对象，创建FormData
    // const formData = new FormData();
    // formData.append("image", file);
    // return request({
    //   url: `${INFO_BASE_URL}/change-avatar/`,
    //   method: "post",
    //   data: formData,
    //   headers: {
    //     "Content-Type": "multipart/form-data",
    //   },
    // });
  },
};

export default InformationAPI;
