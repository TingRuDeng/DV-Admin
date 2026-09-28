from django.db import migrations
from django.db.models import Q


DICTIONARY_PERMISSION_CODES = ("system:dicts:", "system:dictitems:")
DICTIONARY_ROUTE_NAMES = ("Dict", "DictData")
DICTIONARY_COMPONENTS = ("system/dict/index", "system/dict/dict-item")


def remove_dictionary_permissions(apps, schema_editor):
    permissions = apps.get_model("system", "Permissions")
    roles = apps.get_model("system", "Roles")
    role_permissions = roles._meta.get_field("permissions").remote_field.through
    dictionary_permissions = permissions.objects.filter(
        Q(route_name__in=DICTIONARY_ROUTE_NAMES)
        | Q(component__in=DICTIONARY_COMPONENTS)
        | Q(perm__startswith=DICTIONARY_PERMISSION_CODES[0])
        | Q(perm__startswith=DICTIONARY_PERMISSION_CODES[1])
    )
    role_permissions.objects.filter(permissions_id__in=dictionary_permissions.values("id")).delete()
    dictionary_permissions.delete()


class Migration(migrations.Migration):
    dependencies = [("system", "0008_operationlog_audit_context")]

    operations = [
        migrations.RunPython(remove_dictionary_permissions, migrations.RunPython.noop),
        migrations.DeleteModel(name="DictItems"),
        migrations.DeleteModel(name="Dicts"),
    ]
