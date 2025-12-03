# tests/test_calc_hash.py
import hashlib
import io
import os
import sys
import logging
import pytest
from pathlib import Path

from collectionToMisc import calc_hash


# ---------- helpers ---------------------------------------------------------

def _write_bytes(path: Path, data: bytes):
    """Utility that writes *data* to *path* and returns the path."""
    path.write_bytes(data)
    return path


# ---------- happy-path tests ------------------------------------------------

@pytest.mark.parametrize(
    "algo, make_hash",
    [
        ("sha3",   hashlib.sha3_256),             # sha3-256
        ("blake2", lambda: hashlib.blake2b(digest_size=64)),  # blake2b/512
    ],
)
def test_calc_hash_correct_for_known_algorithms(tmp_path, algo, make_hash):
    """The function returns the same digest that hashlib produces."""
    data = b"pytest-rules!"
    path = _write_bytes(tmp_path / "sample.bin", data)

    expected = make_hash()
    expected.update(data)
    expected_hex = expected.hexdigest()

    assert calc_hash(path, algo) == expected_hex


def test_calc_hash_is_deterministic(tmp_path):
    """Hashing the *same* file twice yields the identical digest."""
    path = _write_bytes(tmp_path / "same.txt", b"same content")
    digest1 = calc_hash(path, "sha3")
    digest2 = calc_hash(path, "sha3")
    assert digest1 == digest2


def test_calc_hash_differs_for_different_files(tmp_path):
    """Two different files must produce different digests."""
    a = _write_bytes(tmp_path / "a.txt", b"abc")
    b = _write_bytes(tmp_path / "b.txt", b"xyz")
    assert calc_hash(a, "blake2") != calc_hash(b, "blake2")


# ---------- error-path tests -----------------------------------------------

def test_unknown_algorithm_exits(tmp_path):
    """An unsupported *algo* string should call sys.exit()."""
    path = _write_bytes(tmp_path / "dummy", b"42")
    with pytest.raises(SystemExit):
        calc_hash(path, "made-up-algo")


def test_missing_file_returns_none(tmp_path):
    """If the file doesn’t exist we expect a warning and a None result."""
    # Choose a path that definitely doesn’t exist
    missing = tmp_path / "does_not_exist.bin"
    assert calc_hash(missing, "sha3") is None


def test_shorten_flag_has_no_effect_on_small_files(tmp_path):
    """`shorten=True` should still compute the correct hash when the file
    is smaller than the 250 MB early-exit threshold."""
    data = b"hello shorten"
    path = _write_bytes(tmp_path / "short.bin", data)

    full = calc_hash(path, "blake2", shorten=False)
    short = calc_hash(path, "blake2", shorten=True)
    assert full == short
