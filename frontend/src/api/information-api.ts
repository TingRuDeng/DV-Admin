import request from "@/utils/request";

const INFO_BASE_URL = "/api/information";

const InformationApi = {
  /** 获取个人中心用户信息 */
  getProfile() {
    return request<any, UserProfile>({
      url: `${INFO_BASE_URL}/profile/`,
      method: "get",
    });
  },

  /** 修改个人中心用户信息 */
  updateProfile(data: ProfileForm) {
    return request({
      url: `${INFO_BASE_URL}/profile/`,
      method: "put",
      data,
    });
  },

  /** 修改个人中心用户密码 */
  changePassword(data: PasswordForm) {
    return request({
      url: `${INFO_BASE_URL}/password`,
      method: "put",
      data,
    });
  },

  /**
   * 修改个人头像
   * @param {FormData | File} file 头像信息
   * @returns {Promise} 修改结果
   */
  updateAvatar(file: FormData | File) {
    // 如果传入的已经是FormData对象，直接使用
    if (file instanceof FormData) {
      return request<any, AvatarInfo>({
        url: `${INFO_BASE_URL}/change-avatar/`,
        method: "post",
        data: file,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
    }
    // 如果传入的是文件对象，创建FormData
    const formData = new FormData();
    formData.append("image", file);
    return request<any, AvatarInfo>({
      url: `${INFO_BASE_URL}/change-avatar/`,
      method: "post",
      data: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
};

export default InformationApi;

/**
 * 用户个人信息
 */
export interface UserProfile {
  /** 用户ID */
  id?: string;
  /** 用户名 */
  username?: string;
  /** 用户昵称 */
  name?: string;
  /** 头像URL */
  avatar?: string;
  /** 性别 */
  gender?: number;
  /** 手机号 */
  mobile?: string;
  /** 邮箱 */
  email?: string;
  /** 部门名称 */
  deptName?: string;
  /** 角色名称，多个使用英文逗号(,)分割 */
  roleNames?: string;
  /** 创建时间 */
  createTime?: Date;
}

/**
 * 修改个人信息表单
 */
export interface ProfileForm {
  /** 用户ID */
  id?: string;
  /** 用户昵称 */
  name?: string;
  /** 性别 */
  gender?: number;
  /** 手机号 */
  mobile?: string;
  /** 邮箱 */
  email?: string;
  /** 头像URL */
  avatar?: string;
}

/**
 * 修改密码表单
 */
export interface PasswordForm {
  /** 旧密码 */
  currentPassword?: string;
  /** 新密码 */
  newPassword?: string;
  /** 确认新密码 */
  confirmPassword?: string;
}

/**
 * 头像信息响应
 */
export interface AvatarInfo {
  /** 头像URL */
  avatar?: string;
}
