from django.apps import AppConfig


class SystemConfig(AppConfig):
    name = 'drf_admin.apps.system'

    def ready(self):
        pass
