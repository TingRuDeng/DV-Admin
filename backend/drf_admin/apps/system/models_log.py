from django.db import models


class OperationLog(models.Model):
    """
    操作日志

    记录用户的写操作行为（请求信息、响应状态、执行时间等）。
    字段与 FastAPI `app.db.models.system_log.OperationLog` 对齐；
    时间字段使用 created_at/updated_at（对外驼峰 createdAt/updatedAt），
    与 FastAPI 及前端 `LogPageVO` 一致，因此不复用 BaseModel 的 create_time/update_time。
    """

    user_id = models.IntegerField(null=True, blank=True, verbose_name="用户ID")
    username = models.CharField(max_length=150, blank=True, default="", verbose_name="用户名")
    name = models.CharField(max_length=50, blank=True, default="", verbose_name="用户姓名")

    operation = models.CharField(max_length=100, blank=True, default="", verbose_name="操作描述")
    method = models.CharField(max_length=10, blank=True, default="", verbose_name="请求方法")
    path = models.CharField(max_length=500, blank=True, default="", verbose_name="请求路径")
    query_params = models.TextField(blank=True, default="", verbose_name="查询参数")

    request_body = models.TextField(blank=True, default="", verbose_name="请求体")
    response_status = models.IntegerField(default=0, verbose_name="响应状态码")
    response_body = models.TextField(blank=True, default="", verbose_name="响应体")

    ip = models.CharField(max_length=50, blank=True, default="", verbose_name="IP地址")
    browser = models.CharField(max_length=100, blank=True, default="", verbose_name="浏览器")
    os = models.CharField(max_length=100, blank=True, default="", verbose_name="操作系统")
    execution_time = models.IntegerField(default=0, verbose_name="执行时间(毫秒)")

    status = models.IntegerField(default=1, verbose_name="状态(1:成功;0:失败)")
    error_msg = models.TextField(blank=True, default="", verbose_name="错误信息")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    objects = models.Manager()

    def __str__(self):
        return f"{self.username} - {self.operation}"

    class Meta:
        db_table = "system_operation_log"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["username"]),
            models.Index(fields=["status"]),
            models.Index(fields=["method"]),
            models.Index(fields=["user_id", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]
