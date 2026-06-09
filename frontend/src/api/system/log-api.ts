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
  /** 获取访问趋势 */
  getVisitTrend(queryParams: VisitTrendQuery) {
    return request<unknown, VisitTrendVO>({
      url: `${LOG_BASE_URL}/visit-trend`,
      method: "get",
      params: queryParams,
    });
  },
  /** 获取访问统计 */
  getVisitStats() {
    return request<unknown, VisitStatsVO>({ url: `${LOG_BASE_URL}/visit-stats`, method: "get" });
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
export interface VisitTrendVO {
  /** 日期列表 */
  dates: string[];
  /** 浏览量(PV) */
  pvList: number[];
  /** 访客数(UV) */
  uvList: number[];
  /** IP数 */
  ipList: number[];
}
export interface VisitTrendQuery {
  /** 开始日期 */
  startDate: string;
  /** 结束日期 */
  endDate: string;
}
export interface VisitStatsVO {
  /** 今日访客数(UV) */
  todayUvCount: number;
  /** 总访客数 */
  totalUvCount: number;
  /** 访客数同比增长率（相对于昨天同一时间段的增长率） */
  uvGrowthRate: number;
  /** 今日浏览量(PV) */
  todayPvCount: number;
  /** 总浏览量 */
  totalPvCount: number;
  /** 同比增长率（相对于昨天同一时间段的增长率） */
  pvGrowthRate: number;
}
