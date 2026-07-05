# 数据权限第一阶段迁移。

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("system", "0004_operationlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="roles",
            name="data_scope",
            field=models.IntegerField(
                choices=[
                    (1, "全部数据"),
                    (2, "仅本人数据"),
                    (3, "本部门数据"),
                    (4, "本部门及以下数据"),
                    (5, "自定义部门数据"),
                ],
                default=1,
                verbose_name="数据权限范围",
            ),
        ),
        migrations.AddField(
            model_name="roles",
            name="data_depts",
            field=models.ManyToManyField(
                blank=True,
                db_table="system_roles_to_system_departments",
                related_name="data_scope_roles",
                to="system.departments",
                verbose_name="数据权限部门",
            ),
        ),
    ]
