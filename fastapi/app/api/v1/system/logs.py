"""
操作日志 API 兼容路由入口。

具体端点已拆分到 `log_routes` 子包；保留本入口以兼容
`app.api.v1.system.logs.router` 的上层注册方式。
"""
from app.api.v1.system.log_routes import router

__all__ = ["router"]
