from lib.release_retrievers import get_latest_release
from config import software_repos

def test_get_release():
    temp = software_repos[0]
    release = get_latest_release(temp["owner"],temp["repo"])
    print(f"\nLatest Release of {temp['repo']}: ", release, "\n")
    assert isinstance(release, str)
