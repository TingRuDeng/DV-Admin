"""
系统操作日志 Schema
"""

from datetime import datetime
from typing import Any, List

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


class OperationLogPageQuery(BaseSchema):
    """操作日志分页查询"""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    username: str | None = Field(default=None, description="用户名")
    operation: str | None = Field(default=None, description="操作描述")
    method: str | None = Field(default=None, description="请求方法")
    status: int | None = Field(default=None, description="状态")
    start_time: datetime | None = Field(default=None, description="开始时间")
    end_time: datetime | None = Field(default=None, description="结束时间")


class OperationLogOut(TimestampSchema):
    """操作日志响应数据"""

    user_id: int | None = Field(default=None, description="用户ID")
    username: str = Field(default="", description="用户名")
    name: str = Field(default="", description="用户姓名")
    operation: str = Field(default="", description="操作描述")
    method: str = Field(default="", description="请求方法")
    path: str = Field(default="", description="请求路径")
    query_params: str = Field(default="", description="查询参数")
    request_body: str = Field(default="", description="请求体")
    response_status: int = Field(default=0, description="响应状态码")
    response_body: str = Field(default="", description="响应体")
    ip: str = Field(default="", description="IP地址")
    browser: str = Field(default="", description="浏览器")
    os: str = Field(default="", description="操作系统")
    execution_time: int = Field(default=0, description="执行时间(毫秒)")
    status: int = Field(default=1, description="状态(1:成功;0:失败)")
    error_msg: str = Field(default="", description="错误信息")


class OperationLogPageResult(BaseSchema):
    """操作日志分页结果"""

    list: List[OperationLogOut] = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总数")

    @property
    def results(self) -> List[OperationLogOut]:
        return self.list

    @property
    def count(self) -> int:
        return self.total


class VisitTrendOut(BaseSchema):
    """访问趋势统计"""

    date: str = Field(description="日期")
    count: int = Field(default=0, description="访问次数")


class VisitStatsOut(BaseSchema):
    """访问统计"""

    total_count: int = Field(default=0, description="总访问次数")
    today_count: int = Field(default=0, description="今日访问次数")
    week_count: int = Field(default=0, description="本周访问次数")
    month_count: int = Field(default=0, description="本月访问次数")
    success_count: int = Field(default=0, description="成功次数")
    fail_count: int = Field(default=0, description="失败次数")
    avg_execution_time: float = Field(default=0, description="平均执行时间(毫秒)")
    top_users: list[dict[str, Any]] = Field(default=[], description="活跃用户TOP10")
    top_paths: list[dict[str, Any]] = Field(default=[], description="热门路径TOP10")
