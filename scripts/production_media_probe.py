"""Real upload and read-only Nginx checks for disposable production image tests."""

from __future__ import annotations

import base64
import json
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def upload_media(backend, api, base_url, docker):
    if backend == "fastapi":
        seed = """
import asyncio
from tortoise import Tortoise
from app.core.config import settings
from app.core.security import create_access_token, hash_new_password
from app.db.models.oauth import Users
async def seed():
    await Tortoise.init(config=settings.tortoise_orm_config)
    user = await Users.create(username='image-smoke', password=await hash_new_password('Isolated image user passphrase'), is_superuser=True, is_active=True)
    print(create_access_token(user.id))
    await Tortoise.close_connections()
asyncio.run(seed())
"""
    else:
        seed = """
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'drf_admin.settings'
django.setup()
from drf_admin.apps.system.models import Users
from rest_framework_simplejwt.tokens import RefreshToken
user = Users.objects.create_user(username='image-smoke', password='Isolated image user passphrase', is_superuser=True)
print(str(RefreshToken.for_user(user).access_token))
"""
    token = docker("exec", api, "python", "-c", seed).splitlines()[-1]
    png = docker(
        "exec",
        api,
        "python",
        "-c",
        "from PIL import Image; from io import BytesIO; import base64; b=BytesIO(); Image.new('RGB',(2,2),'red').save(b,format='PNG'); print(base64.b64encode(b.getvalue()).decode())",
    )
    content = base64.b64decode(png)
    boundary = "DVAdminImageSmokeBoundary"
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="smoke.png"\r\nContent-Type: image/png\r\n\r\n'.encode()
        + content
        + f"\r\n--{boundary}--\r\n".encode()
    )
    request = Request(
        base_url + "/api/v1/information/change-avatar/",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    with urlopen(request, timeout=15) as response:
        data = json.load(response)["data"]
    path = urlsplit(data["url"]).path
    assert path.startswith("/media/avatar/")
    print(
        f"{backend}: authenticated image upload through production Nginx: OK",
        flush=True,
    )
    return path, content


def assert_media_read(base_url, path, expected):
    with urlopen(base_url + path, timeout=10) as response:
        assert response.status == 200
        assert response.read() == expected
