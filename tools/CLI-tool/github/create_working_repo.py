import typer
import glob
import subprocess
import sys
import os
import shutil
import yaml

# Define the Typer app
app = typer.Typer()
main_branch = ""

# Use Typer to define repo_name as an argument
@app.command()
def main(repo_name: str, org_name: str):
    """
    Main function to create a GitLab repository, set up structure, and configure secrets.
    """
    print(f"Working with repository: {repo_name}")

    print("Checking if GitLab CLI is installed...")
    check_gl_installed()

    print("Creating a new repository...")
    create_repo(repo_name, org_name)

    print("Pushing the repository to GitLab...")
    push_repo()

    print("Creating branches...")
    create_branches()

    print("Adding branch specific files...")
    copy_files()

    print("Setting up the default branch...")
    set_default_branch(repo_name, org_name)

    print("Setting up the configuration...")
    set_config(repo_name, org_name)


def check_gl_installed():
    """Check if GitLab CLI is installed."""
    try:
        result = subprocess.run(["gl", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            typer.echo("GitLab CLI (gl) is not installed.")
            typer.echo("Do you want to install GitLab CLI? (y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                if sys.platform == "darwin":
                    subprocess.run(["brew", "install", "gl"], check=True)
                elif sys.platform == "linux":
                    subprocess.run(["sudo", "apt", "install", "gl"], check=True)
                else:
                    typer.echo("Unsupported OS. Please install GitLab CLI manually.")
                    sys.exit(1)
            else:
                typer.echo("GitLab CLI (gl) is required. Exiting...")
                sys.exit(1)
    except FileNotFoundError:
        typer.echo("GitLab CLI (gl) is not installed.")
        sys.exit(1)


def check_repo(repo_name, org_name):
    """Check if repository already exists."""
    result = subprocess.run(f"gl repo view {org_name}/{repo_name}", shell=True, capture_output=True)
    return result.returncode == 0


def create_repo(repo_name, org_name):
    """Create a new GitLab repository."""
    result = subprocess.run("gl auth status", shell=True, capture_output=True, text=True)

    if "Logged in to gitlab.com" not in result.stdout:
        subprocess.run("gl auth login", shell=True)

    if not check_repo(repo_name, org_name):
        subprocess.run(f'gl repo create {org_name}/{repo_name} --public --description "Upstream repository" --clone', shell=True)
        os.chdir(repo_name)
    else:
        typer.echo("Repository already exists.")

        repos = subprocess.run('ls -a', shell=True, capture_output=True, text=True).stdout.split()
        if repo_name not in repos:
            subprocess.run(f'git clone https://gitlab.com/{org_name}/{repo_name}.git', shell=True)
            os.chdir(repo_name)
        else:
            os.chdir(repo_name)

def push_repo():
    """Push the repository to GitLab."""
    main_branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
    main_branch = main_branch.stdout.strip()
    print("Current branch:", main_branch)
    subprocess.run(f'echo Readme > README.md', shell=True)
    subprocess.run(["git", 'add', '.'], check=True)
    subprocess.run(["git", 'commit', '-m', '"Initial commit"'], check=True)
    subprocess.run(["git", 'push', 'origin', main_branch], check=True)


def create_branches():
    """Create branches if they don't already exist."""
    
    results = subprocess.run("git branch -a", shell=True, capture_output=True, text=True)
    existing_branches = results.stdout.splitlines()

    branches_to_create = ["development", "staging", "production"]
    for branch in branches_to_create:
        if branch not in existing_branches:
            subprocess.run(f'git checkout -b {branch}', shell=True)
            current_branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)

            print("Current branch:", current_branch.stdout)
            subprocess.run(f'git push --set-upstream origin {branch}', shell=True)
            print(f"Branch '{branch}' created successfully.")


def copy_files():
    """Copy branch-specific files."""

    try:
        result = subprocess.run("git checkout development", capture_output=True, shell=True)
        if "did not match any file(s) known to git" in result.stderr.decode():
            subprocess.run("git checkout -b development", shell=True)
        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/development/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/development/* .", shell=True)
        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/common/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/common/* .", shell=True)
        subprocess.run("git add .", shell=True)
        subprocess.run("git commit -m 'Add branch specific files'", shell=True)
        subprocess.run("git push --set-upstream origin development", shell=True)
    except FileNotFoundError:
        typer.echo("Failed to create branch 'development'. Exiting...")
        sys.exit(1)

    try:
        result = subprocess.run("git checkout production", capture_output=True, shell=True)
        if "did not match any file(s) known to git" in result.stderr.decode():
            subprocess.run("git checkout  main", shell=True)
            subprocess.run("git checkout -b production", shell=True)

        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/production/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/production/* .", shell=True)
        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/common/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/common/* .", shell=True)
        subprocess.run("git add .", shell=True)
        subprocess.run("git commit -m 'Add production files'", shell=True)
        subprocess.run("git push --set-upstream origin production", shell=True)

    except FileNotFoundError:
        typer.echo("Failed to create branch 'production'. Exiting...")
        sys.exit(1)

    try:
        result = subprocess.run("git checkout staging", capture_output=True, shell=True)
        if "did not match any file(s) known to git" in result.stderr.decode():
            subprocess.run("git checkout  main", shell=True)
            subprocess.run("git checkout -b staging", shell=True)

        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/staging/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/staging/* .", shell=True)
        subprocess.run("cp -r ../oss-mlops-platform/tools/CLI-tool/files/common/.[!.]* ../oss-mlops-platform/tools/CLI-tool/files/common/* .", shell=True)
        subprocess.run("git add .", shell=True)
        subprocess.run("git commit -m 'Add staging files'", shell=True)
        subprocess.run("git push --set-upstream origin staging", shell=True)

    except FileNotFoundError:
        typer.echo("Failed to create branch 'staging'. Exiting...")
        sys.exit(1)

#for deleting the main branch
def delete_extra_branch():
    output = subprocess.run("git remote show origin", text=True,shell=True, capture_output=True)
    existing_branches = output.stdout.splitlines()
    branch_to_be_delete = ""
    for branch in existing_branches:
        if "HEAD" in branch:
            branch_to_be_delete = branch.split()[2]
    if branch_to_be_delete:
        subprocess.run(["git", "push", "origin", "--delete", branch_to_be_delete], capture_output=True, text=True,shell=True)
        

def set_default_branch(repo_name, org_name):
    delete_extra_branch()
    """Set the default branch to development."""
    try:
        subprocess.run(f"gl api -X PATCH repos/{org_name}/{repo_name} -f default_branch=development", shell=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error setting default branch: {e.stderr}")
    except FileNotFoundError:
        typer.echo("Failed to set default branch to 'development'.")

def set_config(repo_name, org_name):
    """Create a config file for GitLab secrets"""

    while True:
        try:
            choice = int(input("Choose an option (1: Interactively create config, 2: Copy an existing config.yaml): "))
            if choice in [1, 2]:
                break
            else:
                print("Invalid choice. Please select 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number (1 or 2).")

    config = None

    if choice == 1:
        print("Specify Kubeflow endpoint (default: http://localhost:8080):")
        kep = input().strip()
        if not kep:
            kep = "http://localhost:8080"

        print("Specify Kubeflow username (default: user@example.com):")
        kun = input().strip()
        if not kun:
            kun = "user@example.com"

        print("Specify Kubeflow password (default: 12341234):")
        kpw = input().strip()
        if not kpw:
            kpw = "12341234"

        print("Specify secret name (default: secret_example):")
        sn = input().strip()
        if not sn:
            sn = "secret_example"

        config = {
            "kep": kep,
            "kun": kun,
            "kpw": kpw,
            "sn": sn,
        }

    elif choice == 2:
        print("Enter path to the existing config.yaml file:")
        file_path = input().strip()
        try:
            with open(file_path, "r") as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)

    with open('config.yaml', 'w') as f:
        yaml.dump(config, f)

if __name__ == "__main__":
    app()
