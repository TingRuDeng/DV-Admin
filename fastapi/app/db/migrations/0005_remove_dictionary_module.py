from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [("models", "0004_oidc_identities")]

    initial = False

    operations = [
        ops.RunSQL(
            "DELETE FROM system_roles_to_system_permissions "
            "WHERE permissions_id IN ("
            "SELECT id FROM system_permissions WHERE "
            "route_name IN ('Dict', 'DictData') "
            "OR component IN ('system/dict/index', 'system/dict/dict-item') "
            "OR perm LIKE 'system:dicts:%' "
            "OR perm LIKE 'system:dictitems:%'"
            ")",
            reverse_sql=ops.RunSQL.noop,
        ),
        ops.RunSQL(
            "DELETE FROM system_permissions WHERE "
            "route_name IN ('Dict', 'DictData') "
            "OR component IN ('system/dict/index', 'system/dict/dict-item') "
            "OR perm LIKE 'system:dicts:%' "
            "OR perm LIKE 'system:dictitems:%'",
            reverse_sql=ops.RunSQL.noop,
        ),
        ops.DeleteModel(name="DictItems"),
        ops.DeleteModel(name="DictData"),
    ]
