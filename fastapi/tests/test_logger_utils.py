import json
from datetime import datetime, timezone

from app.utils.logger import JSONLogFormatter


def test_json_log_formatter_escapes_braces_for_loguru_format_map():
    formatter = JSONLogFormatter()
    rendered = formatter.format(
        {
            "time": datetime.now(timezone.utc),
            "level": type("Level", (), {"name": "INFO", "no": 20})(),
            "message": 'payload {"a": 1}',
            "name": "test.logger",
            "module": "test_module",
            "function": "test_function",
            "line": 12,
            "extra": {},
            "exception": None,
        }
    )

    formatted = rendered.format_map(
        {
            "timestamp": "unused",
            "level": "unused",
            "message": "unused",
            "logger": "unused",
            "module": "unused",
            "function": "unused",
            "line": "unused",
            "app": "unused",
            "env": "unused",
        }
    )

    payload = json.loads(formatted)
    assert payload["message"] == 'payload {"a": 1}'
    assert payload["level"] == "INFO"
