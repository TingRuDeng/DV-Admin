/**
 * API响应码枚举
 */
export const enum ApiCodeEnum {
  /**
   * 成功
   */
  SUCCESS = 20000,
  /**
   * 错误
   */
  ERROR = 40000,

  /**
   * 访问令牌无效或过期
   */
  ACCESS_TOKEN_INVALID = 40001,

  /**
   * 刷新令牌无效或过期
   */
  REFRESH_TOKEN_INVALID = 40002,
}
