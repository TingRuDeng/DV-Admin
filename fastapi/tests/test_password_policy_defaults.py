"""The copied deployment example must not silently shorten passphrases in CI."""
from pathlib import Path

from dotenv import dotenv_values


def test_example_password_policy_matches_supported_defaults():
    example = dotenv_values(Path(__file__).resolve().parents[1] / ".env.example")
    assert example["PASSWORD_MIN_LENGTH"] == "15"
    assert example["PASSWORD_MAX_LENGTH"] == "128"
