from lib.iac_retrievers import get_current_version
from config import iac_repos

def test_get_current_version():
    temp = iac_repos[0]
    image_version = get_current_version(temp["owner"],temp["repo"], temp["to_check"][0]["file_path"], temp["to_check"][0]["software"])
    print(f"\nLatest Release of {temp['to_check'][0]['software']} in {temp['repo']}: ", image_version, "\n")
    assert isinstance(image_version,str)
