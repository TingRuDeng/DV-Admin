from tortoise import fields, migrations
from tortoise.indexes import Index
from tortoise.migrations import operations as ops


async def restore_sqlite_operation_log_indexes(apps, schema_editor):
    if schema_editor.DIALECT != "sqlite":
        return

    operation_log = apps.get_model("models", "OperationLog")
    for index in operation_log._meta.indexes:
        await schema_editor.add_index(operation_log, index)


class Migration(migrations.Migration):
    dependencies = [("models", "0002_auto_20260725_2230")]

    initial = False

    operations = [
        ops.RunPython(
            ops.RunPython.noop,
            reverse_code=restore_sqlite_operation_log_indexes,
        ),
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
                null=True,
                description="结构化请求上下文",
            ),
        ),
        ops.RunSQL(
            "UPDATE system_operation_log "
            "SET request_context = '{}' "
            "WHERE request_context IS NULL",
            reverse_sql=ops.RunSQL.noop,
        ),
        ops.AlterField(
            model_name="OperationLog",
            name="request_context",
            field=fields.JSONField(
                description="结构化请求上下文",
            ),
        ),
        ops.RunPython(
            restore_sqlite_operation_log_indexes,
            reverse_code=ops.RunPython.noop,
        ),
        ops.AddIndex(
            model_name="OperationLog",
            index=Index(fields=["object_type", "object_id"]),
        ),
    ]
