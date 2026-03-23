"""
操作日志 API
"""
from datetime import datetime

from fastapi import APIRouter, Path, Query, Request

from app.api.deps import require_permissions
from app.db.models.oauth import Users
from app.schemas.base import ResponseModel
from app.schemas.system import (
    OperationLogPageResult,
    VisitStatsOut,
    VisitTrendOut,
)
from app.services.system.log_service import log_service

router = APIRouter()


@router.get(
    "/page",
    response_model=ResponseModel[OperationLogPageResult],
    summary="获取操作日志分页列表",
    description="""
## 获取操作日志分页列表

分页查询系统操作日志，支持多条件筛选。

### 请求参数
- `page` (可选): 页码，默认 1，最小值 1
- `pageSize` (可选): 每页数量，默认 10，范围 1-100
- `username` (可选): 用户名，模糊匹配
- `operation` (可选): 操作描述，模糊匹配
- `method` (可选): 请求方法（GET/POST/PUT/DELETE/PATCH）
- `status` (可选): 状态（1: 成功, 0: 失败）
- `startTime` (可选): 开始时间，ISO 8601 格式
- `endTime` (可选): 结束时间，ISO 8601 格式

### 权限要求
- 需要 `system:logs:query` 权限

### 响应数据
返回分页结果：
- `total`: 总记录数
- `list`: 日志列表，每条日志包含：
  - `id`: 日志ID
  - `userId`: 用户ID
  - `username`: 用户名
  - `name`: 用户姓名
  - `operation`: 操作描述
  - `method`: 请求方法
  - `path`: 请求路径
  - `queryParams`: 查询参数
  - `requestBody`: 请求体
  - `responseStatus`: 响应状态码
  - `responseBody`: 响应体
  - `ip`: IP地址
  - `browser`: 浏览器
  - `os`: 操作系统
  - `executionTime`: 执行时间（毫秒）
  - `status`: 状态（1: 成功, 0: 失败）
  - `errorMsg`: 错误信息
  - `createdAt`: 创建时间
  - `updatedAt`: 更新时间

### 错误码
- `401`: 未授权
- `403`: 权限不足
    """,
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": {
                            "total": 150,
                            "list": [
                                {
                                    "id": 1,
                                    "userId": 1,
                                    "username": "admin",
                                    "name": "管理员",
                                    "operation": "用户登录",
                                    "method": "POST",
                                    "path": "/api/v1/oauth/login/",
                                    "queryParams": "",
                                    "requestBody": "{\"username\":\"admin\"}",
                                    "responseStatus": 200,
                                    "responseBody": "{\"code\":20000}",
                                    "ip": "192.168.1.100",
                                    "browser": "Chrome 120.0",
                                    "os": "Windows 10",
                                    "executionTime": 156,
                                    "status": 1,
                                    "errorMsg": "",
                                    "createdAt": "2024-01-01T12:00:00Z",
                                    "updatedAt": "2024-01-01T12:00:00Z"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
)
async def get_log_page(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    username: str | None = Query(None, description="用户名"),
    operation: str | None = Query(None, description="操作描述"),
    method: str | None = Query(None, description="请求方法"),
    status: int | None = Query(None, description="状态"),
    start_time: datetime | None = Query(None, description="开始时间"),
    end_time: datetime | None = Query(None, description="结束时间"),
    current_user: Users = require_permissions("system:logs:query"),
):
    data = await log_service.get_page(
        page=page,
        page_size=page_size,
        username=username,
        operation=operation,
        method=method,
        status=status,
        start_time=start_time,
        end_time=end_time,
    )
    return ResponseModel.success(data=data)


@router.get(
    "/visit-trend",
    response_model=ResponseModel[list[VisitTrendOut]],
    summary="获取访问趋势统计",
    description="""
## 获取访问趋势统计

获取指定日期范围内的每日访问次数统计，用于绘制趋势图表。

### 请求参数
- `startDate` (可选): 开始日期，ISO 8601 格式，默认为 7 天前
- `endDate` (可选): 结束日期，ISO 8601 格式，默认为今天

### 权限要求
- 需要 `system:logs:query` 权限

### 响应数据
返回每日访问统计列表：
- `date`: 日期（YYYY-MM-DD 格式）
- `count`: 访问次数

### 使用场景
- 首页展示访问趋势图
- 分析系统使用情况
- 监控异常流量

### 错误码
- `401`: 未授权
- `403`: 权限不足
    """,
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": [
                            {"date": "2024-01-01", "count": 1250},
                            {"date": "2024-01-02", "count": 1580},
                            {"date": "2024-01-03", "count": 1320},
                            {"date": "2024-01-04", "count": 1450},
                            {"date": "2024-01-05", "count": 1680},
                            {"date": "2024-01-06", "count": 980},
                            {"date": "2024-01-07", "count": 1120}
                        ]
                    }
                }
            }
        }
    }
)
async def get_visit_trend(
    request: Request,
    start_date: datetime | None = Query(None, description="开始日期"),
    end_date: datetime | None = Query(None, description="结束日期"),
    current_user: Users = require_permissions("system:logs:query"),
):
    data = await log_service.get_visit_trend(
        start_date=start_date,
        end_date=end_date,
    )
    return ResponseModel.success(data=data)


@router.get(
    "/visit-stats",
    response_model=ResponseModel[VisitStatsOut],
    summary="获取访问统计",
    description="""
## 获取访问统计数据

获取系统访问的综合统计数据，用于首页数据展示。

### 权限要求
- 需要 `system:logs:query` 权限

### 响应数据
返回综合统计数据：
- `totalCount`: 总访问次数
- `todayCount`: 今日访问次数
- `weekCount`: 本周访问次数
- `monthCount`: 本月访问次数
- `successCount`: 成功次数
- `failCount`: 失败次数
- `avgExecutionTime`: 平均执行时间（毫秒）
- `topUsers`: 活跃用户 TOP10
  - `username`: 用户名
  - `name`: 姓名
  - `count`: 访问次数
- `topPaths`: 热门路径 TOP10
  - `path`: 路径
  - `count`: 访问次数

### 使用场景
- 首页数据卡片展示
- 系统监控大屏
- 运营数据分析

### 错误码
- `401`: 未授权
- `403`: 权限不足
    """,
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "success",
                        "data": {
                            "totalCount": 50000,
                            "todayCount": 1250,
                            "weekCount": 8500,
                            "monthCount": 32000,
                            "successCount": 48500,
                            "failCount": 1500,
                            "avgExecutionTime": 125.5,
                            "topUsers": [
                                {"username": "admin", "name": "管理员", "count": 5200},
                                {"username": "zhangsan", "name": "张三", "count": 3200}
                            ],
                            "topPaths": [
                                {"path": "/api/v1/oauth/login/", "count": 8500},
                                {"path": "/api/v1/system/users/", "count": 5200}
                            ]
                        }
                    }
                }
            }
        }
    }
)
async def get_visit_stats(
    request: Request,
    current_user: Users = require_permissions("system:logs:query"),
):
    data = await log_service.get_visit_stats()
    return ResponseModel.success(data=data)


@router.delete("/{ids}", response_model=ResponseModel[None])
async def delete_logs(
    request: Request,
    ids: str,
    current_user: Users = require_permissions("system:logs:delete"),
):
    """
    批量删除操作日志

    Args:
        ids: 日志ID列表，多个ID用逗号分隔，如: 1,2,3
    """
    id_list = [int(x) for x in ids.split(",") if x.strip()]
    deleted_count = await log_service.delete_by_ids(id_list)
    return ResponseModel.success(message=f"成功删除 {deleted_count} 条日志")


@router.delete(
    "/clear/{days}",
    response_model=ResponseModel[None],
    summary="清理历史日志",
    description="""
## 清理指定天数之前的日志

批量删除指定天数之前的历史日志，用于定期维护。

### 路径参数
- `days` (必填): 保留天数，最小值 1，将删除此天数之前的所有日志

### 权限要求
- 需要 `system:logs:delete` 权限

### 业务规则
1. 删除操作不可恢复
2. 建议保留最近 30-90 天的日志
3. 执行前建议先导出备份
4. 大量数据删除可能耗时较长

### 使用场景
- 定期清理历史数据
- 释放数据库存储空间
- 数据归档维护

### 推荐策略
- 开发环境：保留 7 天
- 测试环境：保留 30 天
- 生产环境：保留 90 天

### 错误码
- `401`: 未授权
- `403`: 权限不足
- `400`: 参数错误
    """,
    responses={
        200: {
            "description": "清理成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 20000,
                        "message": "成功清理 1250 条历史日志",
                        "data": None
                    }
                }
            }
        }
    }
)
async def clear_old_logs(
    request: Request,
    days: int = Path(..., ge=1, description="保留天数"),
    current_user: Users = require_permissions("system:logs:delete"),
):
    deleted_count = await log_service.clear_old_logs(days=days)
    return ResponseModel.success(message=f"成功清理 {deleted_count} 条历史日志")
