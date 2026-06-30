import request from "@/utils/request";

const LOG_BASE_URL = "/api/system/logs";

const LogAPI = {
  /** 获取日志分页列表 */
  getPage(queryParams: LogPageQuery) {
    return request<unknown, PageResult<LogPageVO[]>>({
      url: `${LOG_BASE_URL}/page`,
      method: "get",
      params: queryParams,
    });
  },
};

export default LogAPI;

export interface LogPageQuery extends PageQuery {
  /** 操作描述 */
  operation?: string;
  /** 开始时间 */
  startTime?: string;
  /** 结束时间 */
  endTime?: string;
}
export interface LogPageVO {
  /** 主键 */
  id: number;
  /** 操作时间 */
  createdAt: string;
  /** 操作人 */
  username: string;
  /** 日志内容 */
  operation: string;
  /** 请求路径 */
  path: string;
  /** 请求方法 */
  method: string;
  /** IP 地址 */
  ip: string;
  /** 浏览器 */
  browser: string;
  /** 终端系统 */
  os: string;
  /** 执行时间(毫秒) */
  executionTime: number;
}
