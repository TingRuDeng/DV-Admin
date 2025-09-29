/**
 * 响应码枚举
 */
export const ResultEnum = {
  /**
   * 成功
   */
  SUCCESS: 200,
  /**
   * 错误
   */
  ERROR: "B0001",

  /**
   * 访问令牌无效或过期
   */
  ACCESS_TOKEN_INVALID: "A0230",

  /**
   * 刷新令牌无效或过期
   */
  REFRESH_TOKEN_INVALID: "A0231",
};

/**
 * 成功响应码列表
 */
export const SUCCESS_CODES = [200, '00000'];

/**
 * 检查响应码是否为成功
 * @param {number|string} code 响应码
 * @returns {boolean} 是否成功
 */
export const isSuccessCode = (code) => {
  return SUCCESS_CODES.includes(code);
};
