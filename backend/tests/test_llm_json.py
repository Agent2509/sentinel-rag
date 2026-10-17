"""extract_json contract: fences tolerated, non-object output must raise."""
import json

import pytest

from app.llm import extract_json


def test_plain_object():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_fenced_object():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_leading_chatter():
    assert extract_json('Here you go: {"a": 1} hope that helps') == {"a": 1}


def test_non_object_raises_so_callers_retry():
    with pytest.raises(json.JSONDecodeError):
        extract_json("[1, 2, 3]")
    with pytest.raises(json.JSONDecodeError):
        extract_json('"just a string"')


def test_garbage_raises():
    with pytest.raises(json.JSONDecodeError):
        extract_json("no json here")
