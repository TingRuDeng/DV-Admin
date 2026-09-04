from tortoise import fields, migrations
from tortoise.fields.db_defaults import SqlDefault
from tortoise.indexes import Index
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [("models", "0002_auto_20260725_2230")]

    initial = False

    operations = [
        ops.AddField(
            model_name="OperationLog",
            name="object_type",
            field=fields.CharField(
                default="",
                db_default="",
                description="业务对象类型",
                max_length=100,
            ),
        ),
        ops.AddField(
            model_name="OperationLog",
            name="object_id",
            field=fields.CharField(
                default="",
                db_default="",
                description="业务对象ID",
                max_length=255,
            ),
        ),
        ops.AddField(
            model_name="OperationLog",
            name="request_context",
            field=fields.JSONField(
                default=dict,
                db_default=SqlDefault("('{}')"),
                description="结构化请求上下文",
            ),
        ),
        ops.AddIndex(
            model_name="OperationLog",
            index=Index(fields=["object_type", "object_id"]),
        ),
    ]
