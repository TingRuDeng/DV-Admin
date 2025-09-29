#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    # 从命令行参数中获取环境，默认为dev
    environment = 'dev'
    # 复制一份sys.argv，以便修改而不影响原始列表
    argv = sys.argv.copy()
    
    # 查找--env参数在任何位置
    if '--env' in argv:
        env_index = argv.index('--env')
        if env_index + 1 < len(argv):
            environment = argv[env_index + 1]
            # 从参数列表中移除--env和环境值
            del argv[env_index:env_index + 2]
    
    # 设置环境变量
    os.environ.setdefault('ENVIRONMENT', environment)
    # 设置Django设置模块为统一的settings.py
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_admin.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(argv)


if __name__ == '__main__':
    main()