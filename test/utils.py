import os


def can_skip_test():
    """Check when a test can run."""
    is_ci = os.getenv("CI") == "true"
    is_main_repo = os.getenv("GITHUB_REPOSITORY") == "opengisch/qgis-plugin-ci"
    if is_ci and is_main_repo:
        # Always run the test on CI
        return False

    if not os.getenv("tx_api_token") or not os.getenv("github_token"):
        # On local, the token must be set
        return True

    return False
