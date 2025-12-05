import os
from datetime import datetime, timezone
import pytest

from compact_approach import collect_file_info   # ← change to your filename


def test_collect_file_info_success(tmp_path):
    # Create a temporary file
    file = tmp_path / "example.TXT"
    content = "hello world"
    file.write_text(content)

    # Call function
    name, ext, size, mtime = collect_file_info(str(file))

    # Assertions
    assert name == "example.TXT"
    assert ext == ".txt"            # lowercased by your function
    assert size == len(content)

    # Check that modified_time is ISO format
    parsed = datetime.fromisoformat(mtime)
    assert isinstance(parsed, datetime)


def test_collect_file_info_nonexistent():
    name, ext = collect_file_info("/does/not/exist/xxx123.txt")

    # Function returns (None, None)
    assert name is None
    assert ext is None
