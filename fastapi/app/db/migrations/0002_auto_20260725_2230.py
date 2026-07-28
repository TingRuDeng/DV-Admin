from tortoise import fields, migrations
from tortoise.indexes import Index
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [('models', '0001_initial')]

    initial = False

    operations = [
        ops.AddField(
            model_name='OperationLog',
            name='request_id',
            field=fields.CharField(
                default='',
                db_default='',
                description='请求ID',
                max_length=64,
            ),
        ),
        ops.AddIndex(
            model_name='OperationLog',
            index=Index(fields=['request_id']),
        ),
    ]
