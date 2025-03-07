from infisical_sdk import InfisicalSDKClient
import sys
import os
from dotenv import load_dotenv
import re
from packaging import version
from packaging.version import InvalidVersion

load_dotenv()

infisical_project = os.getenv("INFISICAL_PROJECT")

def setup_infisical_client():
    try:
        client = InfisicalSDKClient(host="https://app.infisical.com")
        client.auth.universal_auth.login(
            os.getenv("INFISICAL_ID"),
            os.getenv("INFISICAL_SECRET")
        )
        return client
    except Exception as e:
        print(f"Error setting up Infisical client: {e}")
        sys.exit(1)

client = setup_infisical_client()

def compare_versions(version1: str, version2: str) -> tuple[bool, bool, bool]:
    version_pattern = r'^v?\d+(\.\d+)*([a-zA-Z])?(-?(alpha|beta|rc)(\.?\d+)?)?(-[a-zA-Z0-9._]+)?$'

    if not version1 or not version2:
        raise InvalidVersion("Version strings cannot be empty")

    if not re.match(version_pattern, version1) or not re.match(version_pattern, version2):
        raise InvalidVersion("Invalid version format")

    def parse_kobo_version(v: str) -> tuple[int, int, int, str]:
        v = v.lstrip('v')

        # Match formats like 2.024.36g or 2.024.25d
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)([a-zA-Z])$', v)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))

            # Extract the numeric part and letter part separately
            patch_str = match.group(3)
            letter = match.group(4)

            # Convert patch to integer
            patch = int(patch_str)

            return major, minor, patch, letter
        return None

    def clean_version(v: str) -> str:
        v = v.lstrip('v')
        base_version = v.split('-', 1)[0]
        pre_release = ''

        if '-alpha' in v:
            pre_release = '-alpha' + (v.split('-alpha')[-1].split('-')[0])
        elif '-beta' in v:
            pre_release = '-beta' + (v.split('-beta')[-1].split('-')[0])
        elif '-rc' in v:
            pre_release = '-rc' + (v.split('-rc')[-1].split('-')[0])

        return base_version + pre_release

    kobo1 = parse_kobo_version(version1)
    kobo2 = parse_kobo_version(version2)

    if kobo1 and kobo2:
        major1, minor1, patch1, letter1 = kobo1
        major2, minor2, patch2, letter2 = kobo2

        v1_tuple = (major1, minor1, patch1, ord(letter1.lower()))
        v2_tuple = (major2, minor2, patch2, ord(letter2.lower()))
        is_newer = v1_tuple > v2_tuple

        # For Kobo versions:
        # Major mismatch: first number differs (e.g., 2.024.36g vs 3.024.36g)
        # Minor mismatch: first digit of third number differs (e.g., 2.024.36g vs 2.024.46g)
        major_mismatch = major1 != major2

        # Extract first digit of the patch number
        patch1_first_digit = int(str(patch1)[0]) if str(patch1) else 0
        patch2_first_digit = int(str(patch2)[0]) if str(patch2) else 0
        minor_mismatch = patch1_first_digit != patch2_first_digit

        return is_newer, major_mismatch, minor_mismatch

    try:
        v1 = version.parse(clean_version(version1))
        v2 = version.parse(clean_version(version2))
    except Exception as e:
        raise InvalidVersion(f"Invalid version format: {str(e)}")

    if v1.base_version == v2.base_version:
        if bool(v1.pre) != bool(v2.pre):
            is_newer = bool(v2.pre)
        else:
            is_newer = v1 > v2
    else:
        is_newer = v1 > v2

    major_mismatch = v1.major != v2.major
    minor_mismatch = v1.minor != v2.minor or v1.major != v2.major

    return is_newer, major_mismatch, minor_mismatch

