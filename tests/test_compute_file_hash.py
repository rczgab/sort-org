import hashlib
import pytest
from compact_approach import compute_file_hash   # ← change to your filename


def test_compute_file_hash_simple(tmp_path):
    # Create a small temporary file
    file = tmp_path / "sample.txt"
    content = b"hello world"
    file.write_bytes(content)

    # Compute hash using your function
    result = compute_file_hash(str(file))

    # Compute reference hash directly using hashlib for correctness
    expected = hashlib.sha3_256(content).hexdigest()

    assert result == expected


def test_compute_file_hash_multiple_chunks(tmp_path):
    # Create a file larger than the chunk size to test chunked reading
    chunk_size = 16
    file = tmp_path / "bigfile.bin"

    data = b"A" * (chunk_size * 3 + 5)  # 3 full chunks + partial chunk
    file.write_bytes(data)

    # Hash with your function
    result = compute_file_hash(str(file), chunk_size=chunk_size)

    # Hash with direct hashlib
    expected = hashlib.sha3_256(data).hexdigest()

    assert result == expected


def test_compute_file_hash_file_not_found():
    # Should return None for missing file
    result = compute_file_hash("/no/such/file/xxx.bin")
    assert result is None

def test_compute_file_hash_empty_file(tmp_path):
    # Create an empty file
    file = tmp_path / "empty.txt"
    file.write_bytes(b"")

    # Hash with your function
    result = compute_file_hash(str(file))

    # Hash with direct hashlib
    expected = hashlib.sha3_256(b"").hexdigest()

    assert result == expected