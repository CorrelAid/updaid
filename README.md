# Updaid

This code implements an automated dependency update checker that runs weekly using Modal to monitor both infrastructure-as-code repositories for outdated dependencies. It sends email reports when major or minor version updates are detected.

Specifically, it compares image versions in docker compose files, Dockerfiles and txt against the latest release in the GitHub repository of a dependency.

## Dev Setup

1. Install uv and create modal account
2. ```uv sync ```
3. ```uv run pre-commit install ```
4. Create .env:
```
INFISICAL_ID=""
INFISICAL_SECRET=""
INFISICAL_PROJECT=""

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=mail@correlaid.org

REPORT_RECIPIENTS=mail@example.com
```
5. Create config.py
```
iac_repos = [
    {
        "repo": "CloudStack",
        "owner": "TechCorp",
        "to_check": [
            {
                "file_path": "ansible/templates/dashboard/docker-compose.yml.j2",
                "software": "dashboard",
            },
            {
                "file_path": "ansible/templates/proxy/docker-compose.yml.j2",
                "software": "proxy",
            },
        ],
    }
]

software_repos = {
    "dashboard": {"owner": "dashboardhq", "repo": "dashboard"},
    "proxy": {"repo": "proxyserver", "owner": "proxytech"},
}


doc_link = link
```

## Deploy to Modal

1. Follow Dev Setup
2. ```modal login```
3. ```uv run modal deploy main```
