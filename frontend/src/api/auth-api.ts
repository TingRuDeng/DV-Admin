import request from "@/utils/request";
const AUTH_BASE_URL = "/api/oauth";

const AuthAPI = {
  /** 登录接口*/
  login(data: LoginFormData) {
    return request<any, LoginResult>({
      url: `${AUTH_BASE_URL}/login/`,
      method: "post",
      data,
    });
  },

  /** 刷新 token 接口*/
  refreshToken(refreshToken: string) {
    return request<any, LoginResult>({
      url: `${AUTH_BASE_URL}/refresh-token/`,
      method: "post",
      params: { refreshToken },
      headers: {
        Authorization: "no-auth",
      },
    });
  },

  /** 退出登录接口 */
  logout() {
    return request({
      url: `${AUTH_BASE_URL}/logout/`,
      method: "post",
    });
  },

  /**
   * 获取当前登录用户信息
   *
   * @returns 登录用户昵称、头像信息，包括角色和权限
   */
  getInfo() {
    return request<any, UserInfo>({
      url: `${AUTH_BASE_URL}/info/`,
      method: "get",
    });
  },

  /** 获取当前用户的路由列表 */
  getRoutes() {
    return request<any, RouteVO[]>({ url: `${AUTH_BASE_URL}/menus/routes/`, method: "get" });
  },

  /** 获取验证码接口*/
  getCaptcha() {
    return request<any, CaptchaInfo>({
      url: `${AUTH_BASE_URL}/captcha/`,
      method: "get",
    });
  },
};

export default AuthAPI;

/** 登录表单数据 */
export interface LoginFormData {
  /** 用户名 */
  username: string;
  /** 密码 */
  password: string;
  /** 验证码缓存key */
  captchaKey: string;
  /** 验证码 */
  captchaCode: string;
  /** 记住我 */
  rememberMe: boolean;
}

/** 登录用户信息 */
export interface UserInfo {
  /** 用户ID */
  id?: string;

  /** 用户名 */
  username?: string;

  /** 昵称 */
  name?: string;

  /** 头像URL */
  avatar?: string;

  /** 角色 */
  roles: string[];

  /** 权限 */
  perms: string[];
}

/** 登录响应 */
export interface LoginResult {
  /** 访问令牌 */
  accessToken: string;
  /** 刷新令牌 */
  refreshToken: string;
  /** 令牌类型 */
  tokenType: string;
  /** 过期时间(秒) */
  expiresIn: number;
}

/** 验证码信息 */
export interface CaptchaInfo {
  /** 验证码缓存key */
  captchaKey: string;
  /** 验证码图片Base64字符串 */
  captchaBase64: string;
}

export interface RouteVO {
  /** 子路由列表 */
  children: RouteVO[];
  /** 组件路径 */
  component?: string;
  /** 路由属性 */
  meta?: Meta;
  /** 路由名称 */
  name?: string;
  /** 路由路径 */
  path?: string;
  /** 跳转链接 */
  redirect?: string;
}

export interface Meta {
  /** 【目录】只有一个子路由是否始终显示 */
  alwaysShow?: boolean;
  /** 是否固定页签 */
  affix?: boolean;
  /** 当前路由激活的菜单项 */
  activeMenu?: string;
  /** 面包屑中是否显示 */
  breadcrumb?: boolean;
  /** 稳定缓存键 */
  cacheKey?: string;
  /** 是否按 query 维度区分缓存实例 */
  cacheByQuery?: boolean | number | string;
  /** 仅按指定 query 键区分缓存实例 */
  cacheQueryKeys?: string[] | string;
  /** 是否隐藏(true-是 false-否) */
  hidden?: boolean;
  /** ICON */
  icon?: string;
  /** 【菜单】是否开启页面缓存 */
  keepAlive?: boolean;
  /** 布局覆盖 */
  layout?: "left" | "top" | "mix";
  /** 附加参数 */
  params?: Record<string, unknown>;
  /** 路由级权限（页面访问语义） */
  perms?: string[] | string;
  /** 兼容旧字段 */
  permissions?: string[] | string;
  /** 路由级角色（页面访问语义） */
  roles?: string[] | string;
  /** 路由title */
  title?: string;
}
