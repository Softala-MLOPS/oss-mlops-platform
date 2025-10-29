import typer
import subprocess
import sys
import os
import json

app = typer.Typer()

GITLAB_CONFIG_FILE = os.path.expanduser("~/.gitlab-cli-config.json")


@app.command()
def main(
    platform: str = typer.Option("gitlab", help="Choose platform: github or gitlab"),
):
    print("Checking GitLab CLI installation...")
    check_glab_installed()
    print("Configuring GitLab authentication...")
    configure_gitlab_auth()


def check_glab_installed():
    """Check if GitLab CLI is installed."""
    try:
        result = subprocess.run(["glab", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            typer.echo("GitLab CLI (glab) is not installed.")
            if typer.confirm("Do you want to install GitLab CLI?"):
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


def configure_gitlab_auth():
    """Configure authentication for a self-hosted GitLab instance."""
    instance_url = typer.prompt(
        "Enter your self-hosted GitLab instance URL (e.g., https://gitlab.example.com)"
    )
    token = typer.prompt(
        "Enter your GitLab private access token (with api scope)", hide_input=True
    )

    try:
        subprocess.run(
            ["glab", "auth", "login", "--hostname", instance_url, "--stdin"],
            input=token,
            text=True,
            check=True,
            capture_output=True,
        )
        typer.echo(f"Successfully authenticated with {instance_url}")

        config = {"instance_url": instance_url, "token": token}
        with open(GITLAB_CONFIG_FILE, "w") as f:
            json.dump(config, f)
        typer.echo(f"Configuration saved to {GITLAB_CONFIG_FILE}")

    except subprocess.CalledProcessError as e:
        typer.echo(f"Failed to authenticate with GitLab: {e.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    app()
