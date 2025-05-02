import os
import subprocess
import json
import sys

import json
import subprocess
import typer

# Define the Typer app
app = typer.Typer()


# Use Typer to define repo_name as an argument
@app.command()
def main(repo_name: str, org_name: str):
    """
    Main function to fetch repo details and fork it.
    """
    fork_repo(repo_name, org_name)


def get_working_repo_name(config_repo_name: str):
    if config_repo_name.startswith("Config-"):
        as_split = config_repo_name.split("-")
        as_split[0] = "Working"
        default_working_repo_name = "-".join(as_split)
        return typer.prompt(
            "Enter unique name for your working repository:",
            type=str,
            default=default_working_repo_name,
        )
    return typer.prompt("Enter unique name for your working repository:", type=str)


def check_working_repo_name_unique(org_name: str, working_repo_name: str):
    try:
        return (
            subprocess.run(
                ["glab", f"repo", "view", f"{org_name}/{working_repo_name}"],
                check=False,
            ).returncode
            != 0
        )

        # Check if the repo ain't found
    except:
        # Yeah we're probably OK?
        return True


def fork_repo(repo_name: str, org_name):
    """Fork the repository using GitLab CLI."""
    working_repo_name = get_working_repo_name(repo_name)

    while not check_working_repo_name_unique(org_name, working_repo_name):
        typer.echo(
            f"The repository name {working_repo_name} is already present in the organization! Please provide a different one."
        )
        working_repo_name = get_working_repo_name(repo_name)

    response = subprocess.run(
        [
            "glab",
            "api",
            f"projects/{org_name}%2F{repo_name}/fork",
            "--field",
            f'path={working_repo_name} namespace_path={org_name}'
        ]
    )

    if response.returncode == 0:
        # this is unecessary cause the response should catch this error already but on the off chance it not ;>?

        # Since we're forking via API, we have to do the wait/clone ourselves

        while True:
            try:
                fork_status_resp = json.loads(subprocess.run(['glab', 'api', f'projects/{org_name}%2F{working_repo_name}/import'], capture_output=True, check=True, text=True).stdout)

                import_status = fork_status_resp["import_status"]
                
                if import_status == "failed":
                    print(f"Fork status failed! Resp: {fork_status_resp}")
                    sys.exit(1337)
                print(f"Fork status: {import_status}")
                if import_status == "finished":
                    break
            except Exception as e:
                print(f"Something went wrong during waiting for fork! Error: {e}")
                sys.exit(1)

        print(f"Cloning repository {working_repo_name}")        
        subprocess.run(["glab", "repo", "clone", f"{org_name}/{working_repo_name}", working_repo_name])

        try:
            os.chdir(working_repo_name)
        except FileNotFoundError:
            print(f"{working_repo_name} does not exist")
            exit(1)
        subprocess.run(["git", "checkout", "-b", "staging", "origin/staging"])
        subprocess.run(["git", "checkout", "-b", "production", "origin/production"])
        subprocess.run(["git", "checkout", "-b", "origin/development"])
        os.chdir("../")
    else:
        print(response)
        print()
        print(
            f"Maybe {repo_name} doesn't exist both in local and remote repo of {org_name}?"
        )
        exit(1)

        # This option was for the older versions of GH in order to clone the forked repo

    # if sys.platform == "darwin":
    #     subprocess.run(f'gh repo fork {owner}/{repo_name} --clone --fork-name "{working_repo_name}" --org {owner}', shell=True)
    # elif sys.platform == "linux":
    #     subprocess.run(f'gh repo fork {owner}/{repo_name} --clone --remote-name {working_repo_name} --org {owner}', shell=True)


if __name__ == "__main__":
    app()
