import requests
import typer


class GitLabClient:
    def __init__(self, instance_url, private_token):
        self.instance_url = instance_url.rstrip("/")
        self.api_url = f"https://{self.instance_url}/api/v4"
        self.private_token = private_token
        self.headers = {"PRIVATE-TOKEN": self.private_token}

    def get_group_id(self, group_name):
        """Get the ID of a GitLab group."""
        response = requests.get(
            f"{self.api_url}/groups",
            headers=self.headers,
            params={"search": group_name},
        )
        response.raise_for_status()
        groups = response.json()
        for group in groups:
            if group["path"] == group_name:
                return group["id"]
        return None

    def create_project(self, project_name, group_id, description):
        """Create a new project in a group."""
        data = {
            "name": project_name,
            "namespace_id": group_id,
            "description": description,
            "visibility": "public",
        }
        response = requests.post(
            f"{self.api_url}/projects", headers=self.headers, json=data
        )
        response.raise_for_status()
        return response.json()

    def get_project(self, project_path):
        """Get a project by its path."""
        response = requests.get(
            f"{self.api_url}/projects/{project_path.replace('/', '%2F')}",
            headers=self.headers,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def fork_project(self, project_id, group_id, fork_name):
        """Fork a project into a group."""
        data = {"namespace_id": group_id, "name": fork_name, "path": fork_name}
        response = requests.post(
            f"{self.api_url}/projects/{project_id}/fork",
            headers=self.headers,
            json=data,
        )
        response.raise_for_status()
        return response.json()

    def set_group_variable(self, group_id, key, value):
        """Set a variable at the group level."""
        data = {"key": key, "value": value}
        response = requests.post(
            f"{self.api_url}/groups/{group_id}/variables",
            headers=self.headers,
            json=data,
        )
        response.raise_for_status()
        return response.json()

    def set_project_default_branch(self, project_id, branch_name):
        """Set the default branch for a project."""
        data = {"default_branch": branch_name}
        response = requests.put(
            f"{self.api_url}/projects/{project_id}", headers=self.headers, json=data
        )
        response.raise_for_status()
        return response.json()
