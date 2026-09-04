import request from "@/utils/request";
import {
  batchDeleteRequest,
  type BatchDeleteObjectId,
  type BatchDeleteResult,
} from "./batch-delete";

const USER_BASE_URL = "/api/system/users";

const UserAPI = {
  /**
   * 获取用户分页列表
   *
   * @param queryParams 查询参数
   */
  getPage(queryParams: UserPageQuery) {
    return request<unknown, PageResult<UserPageVO[]>>({
      url: `${USER_BASE_URL}/`,
      method: "get",
      params: queryParams,
    });
  },

  /**
   * 获取用户表单详情
   *
   * @param userId 用户ID
   * @returns 用户表单详情
   */
  getFormData(userId: string) {
    return request<unknown, UserForm>({
      url: `${USER_BASE_URL}/${userId}/`,
      method: "get",
    });
  },

  /**
   * 添加用户
   *
   * @param data 用户表单数据
   */
  create(data: UserForm) {
    return request({
      url: `${USER_BASE_URL}/`,
      method: "post",
      data,
    });
  },

  /**
   * 修改用户
   *
   * @param id 用户ID
   * @param data 用户表单数据
   */
  update(id: string, data: UserForm) {
    return request({
      url: `${USER_BASE_URL}/${id}/`,
      method: "put",
      data,
    });
  },

  /**
   * 修改用户密码
   *
   * @param id 用户ID
   * @param password 新密码
   * @param confirmPassword 确认新密码
   */
  resetPassword(id: string, password: string, confirmPassword: string) {
    return request({
      url: `${USER_BASE_URL}/${id}/password/reset/`,
      method: "put",
      data: {
        password,
        confirm_password: confirmPassword,
      },
    });
  },

  /** 批量删除用户并返回逐条处理结果。 */
  deleteByIds(ids: readonly BatchDeleteObjectId[]) {
    return request<unknown, BatchDeleteResult>({
      url: `${USER_BASE_URL}/`,
      method: "delete",
      data: batchDeleteRequest(ids),
    });
  },

  /** 重试单个或多个可重试的用户删除失败项。 */
  retryBatchDelete(ids: readonly BatchDeleteObjectId[]) {
    return request<unknown, BatchDeleteResult>({
      url: `${USER_BASE_URL}/batch-delete/retry/`,
      method: "post",
      data: batchDeleteRequest(ids),
    });
  },

  /** 下载用户导入模板 */
  downloadTemplate() {
    return request<unknown, EncodedFile>({
      url: `${USER_BASE_URL}/template`,
      method: "get",
    });
  },

  /** 导出当前权限范围内的用户 */
  export() {
    return request<unknown, EncodedFile>({
      url: `${USER_BASE_URL}/export/`,
      method: "post",
    });
  },

  /**
   * 导入用户
   *
   * @param deptId 默认部门ID
   * @param file 导入文件
   */
  import(deptId: string | number | undefined, file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return request<unknown, UserImportResult>({
      url: `${USER_BASE_URL}/import`,
      method: "post",
      params: deptId == null ? undefined : { deptId },
      data: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  /**
   *  获取用户下拉列表
   */
  getOptions() {
    return request<unknown, OptionType[]>({
      url: `${USER_BASE_URL}/options`,
      method: "get",
    });
  },
};

export default UserAPI;

export interface EncodedFile {
  filename: string;
  content: string;
  contentType: string;
}

export interface UserImportResult {
  invalidCount: number;
  validCount: number;
  messageList: string[];
}

/**
 * 用户分页查询对象
 */
export interface UserPageQuery extends PageQuery {
  /** 搜索关键字 */
  search?: string;

  /** 用户状态 */
  isActive?: number;

  /** 部门ID */
  deptId?: string;

  /** 开始时间 */
}

/** 用户分页对象 */
export interface UserPageVO {
  /** 用户ID */
  id: string;
  /** 用户头像URL */
  avatar?: string;
  /** 创建时间 */
  /** 部门名称 */
  deptName?: string;
  /** 用户邮箱 */
  email?: string;
  /** 性别 */
  gender?: number;
  /** 手机号 */
  mobile?: string;
  /** 用户昵称 */
  name?: string;
  /** 角色名称，多个使用英文逗号(,)分割 */
  roleNames?: string;
  /** 角色ID集合 */
  roles?: number[];
  /** 用户状态(1:启用;0:禁用) */
  isActive?: number;
  /** 用户名 */
  username?: string;
}

/** 用户表单类型 */
export interface UserForm {
  /** 用户ID */
  id?: string;
  /** 用户头像 */
  avatar?: string;
  /** 部门ID */
  deptId?: number | string;
  /** 邮箱 */
  email?: string;
  /** 性别 */
  gender?: number;
  /** 手机号 */
  mobile?: string;
  /** 昵称 */
  name?: string;
  /** 角色ID集合 */
  roles?: number[];
  /** 角色名称，多个使用英文逗号(,)分割 */
  roleNames?: string;
  /** 用户状态(1:正常;0:禁用) */
  isActive?: number;
  /** 用户名 */
  username?: string;
}
