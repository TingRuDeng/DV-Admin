from tortoise import fields, migrations
from tortoise.fields.base import OnDelete
from tortoise.indexes import Index
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [('models', '0003_operationlog_audit_context')]

    initial = False

    operations = [
        ops.CreateModel(
            name='OidcIdentity',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True, description='主键ID')),
                ('created_at', fields.DatetimeField(description='创建时间', auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(description='更新时间', auto_now=True, auto_now_add=False)),
                ('issuer', fields.CharField(description='身份提供方 issuer', max_length=255)),
                ('subject', fields.CharField(description='身份提供方用户标识 sub', max_length=255)),
                ('user', fields.ForeignKeyField('models.Users', source_field='user_id', description='绑定的本地用户', db_constraint=True, to_field='id', related_name='oidc_identities', on_delete=OnDelete.CASCADE)),
                ('email', fields.CharField(default='', description='绑定时的邮箱', max_length=254)),
                ('last_login_at', fields.DatetimeField(null=True, description='最后单点登录时间', auto_now=False, auto_now_add=False)),
            ],
            options={'table': 'oauth_oidc_identities', 'app': 'models', 'unique_together': (('issuer', 'subject'),), 'indexes': [Index(fields=['user_id'])], 'pk_attr': 'id', 'table_description': '单点登录身份模型'},
            bases=['BaseModel'],
        ),
    ]
