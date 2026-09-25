from django.conf import settings
from django.db import models

from drf_admin.utils.models import BaseModel


class OidcIdentity(BaseModel):
    """单点登录外部身份与本地用户的绑定关系"""

    issuer = models.CharField(max_length=255, verbose_name="身份提供方")
    subject = models.CharField(max_length=255, verbose_name="外部用户标识")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="oidc_identities",
        verbose_name="本地用户",
    )
    email = models.CharField(max_length=254, default="", blank=True, verbose_name="登录邮箱")
    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name="最近登录时间")

    class Meta:
        db_table = "oauth_oidc_identities"
        verbose_name = "单点登录身份"
        verbose_name_plural = verbose_name
        unique_together = (("issuer", "subject"),)

    def __str__(self):
        return f"{self.issuer}|{self.subject}"
