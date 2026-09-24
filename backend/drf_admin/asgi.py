"""ASGI config for drf_admin project.

The exported application is the Channels router used by ASGI deployments.
"""

from drf_admin.routing import application

__all__ = ["application"]
