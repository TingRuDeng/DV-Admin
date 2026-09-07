from unittest.mock import patch

from app.main import main


def test_console_entrypoint_loads_installed_application():
    with patch("uvicorn.run") as run:
        main()
    assert run.call_args.args == ("app.main:app",)
    assert run.call_args.kwargs["proxy_headers"] is False
