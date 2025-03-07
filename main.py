import modal
from config import software_repos, iac_repos
from lib import checker
from lib.email_helpers import send_report

app = modal.App("updaid")

image = (
    modal.Image.debian_slim()
    .add_local_file("requirements.txt", "/root/requirements.txt", copy=True)
    .run_commands("pip install uv && uv pip install --system -r /root/requirements.txt")
    .add_local_python_source("config", "lib")
)


@app.function(
    image=image,
    secrets=[modal.Secret.from_dotenv(__file__)],
    schedule=modal.Period(weeks=1),
)
def f():
    results = checker(iac_repos, software_repos)
    action_required = False
    for repo_dict in results:
        for _, updates in repo_dict.items():
            for update in updates:
                if (
                    update["mismatch_type"]
                    in [
                        "major",
                        "minor",
                    ]
                    or update["error"] is True
                ):
                    action_required = True
                    break

            if action_required:
                break
        if action_required:
            break

    if action_required:
        print("Major or minor updates found, sending report...")
        send_report(results)
    else:
        print("No major or minor updates found, no report needed")

    return results


@app.local_entrypoint()
def main():
    print(f.remote())
