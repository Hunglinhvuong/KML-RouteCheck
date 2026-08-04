import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.telegram_bot import parse_allowed_chat_ids


def test_parse_allowed_chat_ids_allows_empty_values():
    assert parse_allowed_chat_ids("") is None
    assert parse_allowed_chat_ids("all") is None
    assert parse_allowed_chat_ids("*") is None


def test_parse_allowed_chat_ids_parses_numbers():
    assert parse_allowed_chat_ids("123,456") == [123, 456]
