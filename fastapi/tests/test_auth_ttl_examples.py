"""Published authentication examples must match the configurable defaults."""

import json
import re
from pathlib import Path

import pytest

from app.core.config import Settings
from app.main import create_app


@pytest.mark.parametrize("action", ["login", "token", "refresh-token"])
def test_openapi_auth_examples_use_default_access_ttl(action):
    operation = create_app().openapi()["paths"][f"/api/v1/oauth/{action}/"]["post"]
    example = operation["responses"]["200"]["content"]["application/json"]["example"]
    assert example["data"]["expiresIn"] == 1800
    assert example["data"]["refreshExpiresIn"] == 604800
    assert "默认 2 小时" not in operation["description"]


def test_published_auth_examples_match_config_defaults():
    assert Settings.model_fields["access_token_expire_minutes"].default * 60 == 1800
    assert Settings.model_fields["refresh_token_expire_days"].default * 86400 == 604800
    document = Path(__file__).parents[2] / "docs" / "API_ENDPOINTS.md"
    examples = [
        json.loads(block)["data"]
        for block in re.findall(r"```json\n(.*?)\n```", document.read_text(), re.S)
        if '"expiresIn"' in block
    ]
    assert len(examples) == 2
    assert all(example["expiresIn"] == 1800 for example in examples)
