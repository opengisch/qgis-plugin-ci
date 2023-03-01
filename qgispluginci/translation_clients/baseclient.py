from typing import NamedTuple


class TranslationConfig(NamedTuple):
    api_token: str
    organization_name: str
    project_slug: str
    resource_file_path: str
    resource_slug: str

    private: bool = False
    project_name: str = None
    i18n_type: str = "QT"
    repository_url: str = None
    source_language_code: str = "en"


class BaseClient:
    def __init__(
        self, config: TranslationConfig, update_string_fcn, create_project: bool = True
    ):
        """
        Parameters
        ----------
        config:
            The config for the Translation platform

        create_project:
            if True, it will create the project, resource and language on Transifex

        """
        self.config = config
        self.login()
        self.project = self.get_project()
        if not self.project and create_project:
            self.project = self.create_project()
            update_string_fcn()
            self.create_resource()

    def login(self):
        raise NotImplementedError

    def get_project(self):
        raise NotImplementedError

    def project_exists(self):
        raise NotImplementedError

    def create_project(self):
        raise NotImplementedError

    def delete_project(self):
        raise NotImplementedError

    def create_resource(self):
        raise NotImplementedError

    def list_resources(self):
        raise NotImplementedError

    def get_resource(self):
        raise NotImplementedError

    def list_languages(self):
        raise NotImplementedError

    def create_language(self, language_code: str):
        raise NotImplementedError

    def update_source_translation(self):
        raise NotImplementedError

    def get_translation(
        self,
        language_code: str,
        path_to_output_file: str,
    ) -> str:
        raise NotImplementedError
