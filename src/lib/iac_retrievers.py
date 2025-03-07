from lib.helpers import client, infisical_project
import requests
import yaml


def extract_version(dockerfile_content):
    for line in dockerfile_content.splitlines():
        if line.startswith("FROM "):
            if " AS " in line:
                continue
            image_part = line.split("FROM ")[1].split()[0]
            if ":" in image_part:
                return image_part.split(":")[1]
    return None


def get_current_version(owner: str, repo: str, path: str, service_name: str):
    access_token = client.secrets.get_secret_by_name(
        secret_name="GITHUB_TOKEN_READ",
        project_id=infisical_project,
        environment_slug="prod",
        secret_path="/",
    ).secretValue

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    content = response.json()
    assert "download_url" in content, "Download URL not found in response"

    response = requests.get(content["download_url"])
    response.raise_for_status()

    if "Dockerfile" in path:
        image_version = extract_version(response.text)
    elif ".txt" in path:
        image_version = response.text
        print(image_version)
    else:
        yaml_content = response.text.replace("{{", "").replace("}}", "")
        parsed_yaml = yaml.safe_load(yaml_content)

        assert "services" in parsed_yaml, "Services section not found in YAML"
        assert service_name in parsed_yaml["services"], (
            f"Service '{service_name}' not found"
        )
        assert "image" in parsed_yaml["services"][service_name], (
            f"Image not specified for service '{service_name}'"
        )

        image_version = parsed_yaml["services"][service_name]["image"].split(":")[-1]
    return image_version
