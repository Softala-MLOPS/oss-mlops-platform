import os
from typing import Mapping, Optional, Tuple


def get_ci_context(environ: Optional[Mapping[str, str]] = None) -> Tuple[str, str]:
    """Return the CI platform and branch for the current environment."""
    if environ is None:
        environ = os.environ

    if environ.get("GITHUB_ACTIONS") == "true":
        return "github-actions", environ.get("GITHUB_REF_NAME") or "unknown-branch"

    if environ.get("BITBUCKET_BUILD_NUMBER") or environ.get("BITBUCKET_BRANCH"):
        return "bitbucket-pipelines", environ.get("BITBUCKET_BRANCH") or "unknown-branch"

    if environ.get("CI") == "true":
        return "gitlab-ci", environ.get("CI_COMMIT_BRANCH") or "unknown-branch"

    return "local", "unknown-branch"