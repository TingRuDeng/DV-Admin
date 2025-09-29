import request from "@/utils/request";

const AUTH_BASE_URL = "/oauth";

const AuthAPI = {
  /** 登录接口*/
  login(data) {
    const formData = new FormData();
    formData.append("username", data.username);
    formData.append("password", data.password);
    formData.append("captchaKey", data.captchaKey);
    formData.append("captchaCode", data.captchaCode);
    return request({
      url: `${AUTH_BASE_URL}/login/`,
      method: "post",
      data: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  /** 刷新 token 接口*/
  refreshToken(refreshToken) {
    return request({
      url: `${AUTH_BASE_URL}/refresh-token/`,
      method: "post",
      params: { refreshToken: refreshToken },
      headers: {
        Authorization: "no-auth",
      },
    });
  },

  /** 注销登录接口 */
  logout() {
    return request({
      url: `${AUTH_BASE_URL}/logout/`,
      method: "post",
    });
  },

  /** 获取验证码接口*/
  getCaptcha() {
    return request({
      url: `${AUTH_BASE_URL}/captcha/`,
      method: "get",
    });
  },

  /**
   * 获取当前登录用户信息
   * @returns {Promise} 登录用户昵称、头像信息，包括角色和权限
   */
  getInfo() {
    return request({
      url: `${AUTH_BASE_URL}/info/`,
      method: "get",
    });
  },

  /**
   * 获取当前用户的路由列表
   * <p/>
   * 无需传入角色，后端解析token获取角色自行判断是否拥有路由的权限
   * @returns {Promise} 路由列表
   */
  getRoutes() {
    return request({
      url: `${AUTH_BASE_URL}/menus/routes/`,
      method: "get",
    });
  },
};

export default AuthAPI;
