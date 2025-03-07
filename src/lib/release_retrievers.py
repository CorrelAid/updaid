from lib.helpers import client, infisical_project
import requests


def get_latest_release(owner, repo):
    access_token = client.secrets.get_secret_by_name(
        secret_name="GITHUB_TOKEN_READ",
        project_id=infisical_project,
        environment_slug="prod",
        secret_path="/",
    ).secretValue

    url = f"https://api.github.com/repos/{owner}/{repo}/releases"

    # Headers
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    releases = response.json()

    assert isinstance(releases, list)
    assert len(releases) > 0
    assert isinstance(releases[0]["prerelease"], bool)

    filtered_releases = [r for r in releases if r["prerelease"] is False]

    sorted_releases = sorted(
        filtered_releases, key=lambda x: x["published_at"], reverse=True
    )

    return sorted_releases[0]["tag_name"]
