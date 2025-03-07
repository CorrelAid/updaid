from lib.helpers import compare_versions
from lib.release_retrievers import get_latest_release
from lib.iac_retrievers import get_current_version


def checker(iac_repos, software_repos):
    """Check for version mismatches between IaC repositories and software repositories."""
    main_lst = []

    for iac in iac_repos:
        repo = iac['repo']
        owner = iac["owner"]
        print(f"Checking software in {repo}")
        result_lst = []

        for to_check in iac["to_check"]:
            try:
                software_name = to_check['software']
                path = to_check['file_path']
                print(f"Checking {software_name} in {path}")

                if software_name not in software_repos:
                    print(f"Warning: {software_name} not found in software_repos configuration")
                    continue

                software_dct = software_repos[software_name]
                latest_version = get_latest_release(software_dct["owner"], software_dct["repo"])
                current_version = get_current_version(owner, repo, path, software_name)

                print(f"Latest: {latest_version}, Current: {current_version}")

                is_newer, major_mismatch, minor_mismatch = compare_versions(
                    latest_version,
                    current_version
                )

                if is_newer and major_mismatch:
                    result_lst.append({
                        "software": software_name,
                        "message": f"Newer major version! - Current: {current_version}, Latest: {latest_version}",
                        "current_version": current_version,
                        "latest_version": latest_version,
                        "mismatch_type": "major"
                    })
                elif is_newer and minor_mismatch:
                    result_lst.append({
                        "software": software_name,
                        "message": f"Newer minor version! - Current: {current_version}, Latest: {latest_version}",
                        "current_version": current_version,
                        "latest_version": latest_version,
                        "mismatch_type": "minor"
                    })

            except Exception as e:
                print(f"Error checking {software_name}: {str(e)}")
                result_lst.append({
                    "software": software_name,
                    "message": f"Error during version check: {str(e)}",
                    "error": True
                })

        main_lst.append({repo: result_lst})

    return main_lst



