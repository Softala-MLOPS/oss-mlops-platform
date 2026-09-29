import sys
import unittest
from pathlib import Path


CLI_TOOL_DIR = Path(__file__).resolve().parents[1]
COMMON_SRC_DIR = CLI_TOOL_DIR / "files" / "common" / "src"
sys.path.insert(0, str(COMMON_SRC_DIR))

from ci_context import get_ci_context


class GetCiContextTests(unittest.TestCase):
    def test_identifies_bitbucket_and_branch(self):
        context = get_ci_context(
            {
                "CI": "true",
                "BITBUCKET_BUILD_NUMBER": "42",
                "BITBUCKET_BRANCH": "development",
            }
        )

        self.assertEqual(context, ("bitbucket-pipelines", "development"))

    def test_identifies_gitlab_and_branch(self):
        context = get_ci_context({"CI": "true", "CI_COMMIT_BRANCH": "staging"})

        self.assertEqual(context, ("gitlab-ci", "staging"))

    def test_identifies_github_and_branch(self):
        context = get_ci_context(
            {"GITHUB_ACTIONS": "true", "GITHUB_REF_NAME": "production"}
        )

        self.assertEqual(context, ("github-actions", "production"))

    def test_identifies_local_run(self):
        context = get_ci_context({})

        self.assertEqual(context, ("local", "unknown-branch"))


if __name__ == "__main__":
    unittest.main()