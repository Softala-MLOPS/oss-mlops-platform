import os
import subprocess
import json
import sys

import json
import subprocess
import typer

# Define the Typer app
app = typer.Typer()
owner = "Softala-MLOPS"

# Use Typer to define repo_name as an argument
@app.command()
def main(repo_name: str):
    """
    Main function to fetch repo details and fork it.
    """
    print(f"Fetching repository information for {repo_name}...")
    repo_owner = owner #get_repo_owner(repo_name)
    fork_repo(repo_name, repo_owner)

#     if repo_owner:
#         print("Forking the repository...")
#         fork_repo(repo_name, repo_owner)
#     else:
#         print("Could not fetch repository information. Exiting...")

# def get_repo_owner(repo_name: str):
#     """Fetch the repository owner using GitHub API."""
#     result = subprocess.run(
#         f"gh api -X GET search/repositories -f q='{repo_name} in:name' --jq '.items[] | {{name, owner: .owner.login}}'",
#         shell=True,
#         capture_output=True,
#         text=True
#     )

#     if result.returncode != 0:
#         print("Error fetching repository information:", result.stderr)
#         return None
    
#     try:
#         print(result.stdout)
#         repo_info_list = [json.loads(line) for line in result.stdout.strip().split('\n')]
#         repo_info = repo_info_list[0]
#         print(f"Repository found: {repo_info}")
#         owner_name = repo_info['owner']
#         return owner_name
#     except json.JSONDecodeError:
#         print("Error decoding repository information")
#         return None

def fork_repo(repo_name: str, owner: str):
    """Fork the repository using GitHub CLI."""
    working_repo_name = typer.prompt("Enter unique name for your working repository", type=str)

    if sys.platform == "darwin":
        subprocess.run(f'gh repo fork {owner}/{repo_name} --clone --fork-name "{working_repo_name}" --org {owner}', shell=True)
    elif sys.platform == "linux":
        subprocess.run(f'gh repo fork {owner}/{repo_name} --clone --remote-name {working_repo_name} --org {owner}', shell=True)

    try:
        os.chdir(working_repo_name)
        subprocess.run(f'gh workflow enable',shell=True, capture_output=True) # Enable GitHub Actions
        print("Repository forked successfully.")
    except FileNotFoundError:
        print("Error enabling workflow for:", working_repo_name)

if __name__ == "__main__":
    app()