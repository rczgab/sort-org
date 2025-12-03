from collectionToMisc import calc_hash
from pathlib import Path

WorkingDir = Path(__file__).parent
algorithm = "blake2"  # Example hash algorithm, can be changed
algorithm2 = "sha3"  # Example hash algorithm, can be changed

def calc_hash_helper(algo):
    # Test with a known file
    test_file = WorkingDir / "testA.jpg"  # Replace with an actual test file path
    test_file2 = WorkingDir / "testB.png"  # Replace with another actual test file path
    expected_hash = "expected_hash_value"  # Replace with the expected hash value for the test file
    hashA = calc_hash(test_file, algo)
    hashA_1 = calc_hash(test_file, algo)
    hashB = calc_hash(test_file2,  algo)
    #assert calc_hash(test_file) == expected_hash, "Hash does not match expected value"
    assert hashA == hashA_1, "Hash should be consistent for the same file"
    assert hashA != hashB, "Hashes should be different for different files"

def test_calc_hash():
    calc_hash_helper(algorithm)
    calc_hash_helper(algorithm2)