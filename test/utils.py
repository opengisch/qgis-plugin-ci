import os


def can_skip_test_github():
    """Check when the Transifex test can run."""
    is_ci = os.getenv("CI") == "true"
    is_main_repo = os.getenv("GITHUB_REPOSITORY") == "opengisch/qgis-plugin-ci"

    if is_ci and is_main_repo:
        return False

    if not os.getenv("github_token"):
        return True

    return False


def can_skip_test_transifex():
    """Check when the Transifex test can run."""
    is_ci = os.getenv("CI") == "true"
    is_main_repo = os.getenv("GITHUB_REPOSITORY") == "opengisch/qgis-plugin-ci"
    is_dependabot = os.getenv("GITHUB_ACTOR") == "dependabot[bot]"

    if is_ci and is_main_repo and not is_dependabot:
        # Always run the test on CI
        return False

    if not os.getenv("tx_api_token"):
        return True

    return False
