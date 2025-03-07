from lib.helpers import compare_versions

def test_compare_versions():
    """Test cases for compare_versions function"""
    test_cases = [
        # version1, version2, expected_newer, expected_major_mismatch, expected_minor_mismatch
        # Different minor versions (8 vs 9)
        ("v2.9.1", "2.8.4-alpine", True, False, True),
        ("2.8.4-alpine", "v2.9.1", False, False, True),
        # Same versions with different formats
        ("v2.9.1", "2.9.1-alpine", False, False, False),

        # Same versions with different suffixes
        ("2.8.4-alpine", "2.8.4-slim", False, False, False),
        ("2.8.4-alpine", "2.8.4", False, False, False),

        # Major and minor version differences
        ("v3.0.0-alpine", "2.9.1", True, True, True),  # 3.0 vs 2.9
        ("2.0.0-alpine", "3.0.0", False, True, True), # 2.0 vs 3.0 (same minor)

       # Kobo version tests
        ("2.024.36g", "2.024.25d", True, False, True),   # different first digit of third number
        ("2.024.25d", "2.024.36g", False, False, True),  #  different first digit of third number

        ("2.024.25d", "3.024.36g", False, True, True),   # Different major versions

        ("2.024.25d", "2.024.25d", False, False, False), # Identical versions

        ("2.024.36g", "2.024.37g", False, False, False),  # Same first digit of third number
        ("2.024.16d", "2.024.14g", True, False, False), # Same first digit of third number 
    ]

    for version1, version2, expected_newer, expected_major, expected_minor in test_cases:
        is_newer, major_mismatch, minor_mismatch = compare_versions(version1, version2)
        assert is_newer == expected_newer, \
            f"Version comparison: Expected {version1} {'>' if expected_newer else '<='} {version2}, got {is_newer}"
        assert major_mismatch == expected_major, \
            f"Major version mismatch: Expected {expected_major} for {version1} vs {version2}, got {major_mismatch}"
        assert minor_mismatch == expected_minor, \
            f"Minor version mismatch: Expected {expected_minor} for {version1} vs {version2}, got {minor_mismatch}"


