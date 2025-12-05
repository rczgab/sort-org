import os
import pytest

# import the function you want to test
from compact_approach import walk_file_system


def test_walk_file_system_single_level(tmp_path):
    # Create test files
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.jpg"
    f1.write_text("hello")
    f2.write_text("world")

    # Run the function
    results = list(walk_file_system(str(tmp_path)))

    # Convert to pure paths to avoid path mismatch issues
    results = set(map(os.path.normpath, results))

    # Expected
    expected = {
        os.path.normpath(str(f1)),
        os.path.normpath(str(f2)),
    }

    assert results == expected


def test_walk_file_system_nested_directories(tmp_path):
    # Create nested structure
    d1 = tmp_path / "dir1"
    d2 = tmp_path / "dir1" / "dir2"
    d2.mkdir(parents=True)

    f1 = d1 / "file1.txt"
    f2 = d2 / "file2.dat"

    f1.write_text("x")
    f2.write_text("y")

    # Run
    results = list(walk_file_system(str(tmp_path)))
    results = set(map(os.path.normpath, results))

    expected = {
        os.path.normpath(str(f1)),
        os.path.normpath(str(f2)),
    }

    assert results == expected


def test_walk_file_system_empty_directory(tmp_path):
    # No files created
    results = list(walk_file_system(str(tmp_path)))
    assert results == []

