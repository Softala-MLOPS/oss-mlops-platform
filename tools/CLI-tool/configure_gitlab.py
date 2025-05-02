import typer
import subprocess
import sys

app = typer.Typer()

@app.command()
def main(platform: str = typer.Option("github", help="Choose platform: github or gitlab")):
    print("Checking GitLab CLI installation...")
    check_glab_installed()
    print("Checking GitLab authentication...")
    check_glab_auth()

def check_glab_installed():
    """Check if GitLab CLI is installed."""
    try:
        result = subprocess.run(["glab", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            typer.echo("GitLab CLI (glab) is not installed.")
            typer.echo("Do you want to install GitLab CLI? (y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                if sys.platform == "darwin":
                    subprocess.run(["brew", "install", "glab"], check=True)
                elif sys.platform == "linux":
                    subprocess.run(["sudo", "apt", "install", "glab"], check=True)
                else:
                    typer.echo("Unsupported OS. Please install GitLab CLI manually.")
                    sys.exit(1)
            else:
                typer.echo("GitLab CLI (glab) is required. Exiting...")
                sys.exit(1)
    except FileNotFoundError:
        typer.echo("GitLab CLI (glab) is not installed.")
        sys.exit(1)

def check_glab_auth():
    """Check if user is authenticated with GitLab."""
    result = subprocess.run("glab auth status", shell=True, capture_output=True, text=True)
    print(f"Dbg: {result.stdout}")
    if "Logged in to gitlab.com" not in result.stdout:
        subprocess.run("glab auth login", shell=True)

if __name__ == "__main__":
    app()
