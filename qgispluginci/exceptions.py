

class TranslationFailed(Exception):
    pass


class TransifexNoResource(Exception):
    pass


class TransifexManyResources(Warning):
    pass


class GithubReleaseNotFound(Exception):
    pass


class GithubReleaseCouldNotUploadAsset(Exception):
    pass


class UncommitedChanges(Exception):
    pass


class ConfigurationNotFound(Exception):
    pass
