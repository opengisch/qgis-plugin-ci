class BuiltResourceInSources(Exception):
    pass


class ConfigurationNotFound(Exception):
    pass


class GithubReleaseCouldNotUploadAsset(Exception):
    pass


class GithubReleaseNotFound(Exception):
    pass


class MissingChangelog(Exception):
    pass


class TransifexManyResources(Warning):
    pass


class TransifexNoResource(Exception):
    pass


class TranslationFailed(Exception):
    pass


class UncommitedChanges(Exception):
    pass
