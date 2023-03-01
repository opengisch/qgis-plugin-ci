import logging
from pathlib import Path

import requests
from transifex.api import transifex_api as tx_api
from transifex.api.jsonapi.exceptions import DoesNotExist

from qgispluginci.translation_clients.baseclient import BaseClient, TranslationConfig

# GLOBALS
logger = logging.getLogger(__name__)


class TransifexClient(BaseClient):
    def __init__(
        self, config: TranslationConfig, update_string_fcn, create_project: bool = True
    ):
        super(TransifexClient, self).__init__(config, update_string_fcn, create_project)

    def login(self):
        tx_api.setup(auth=self.config.api_token)
        self.organization = self.get_organization()
        logger.info(f"Logged in as organization: {self.config.organization_name}")

    def get_organization(self):
        return tx_api.Organization.get(slug=self.config.organization_name)

    def get_project(self):
        try:
            return (
                self.get_organization()
                .fetch("projects")
                .get(slug=self.config.project_slug)
            )
        except DoesNotExist:
            return None

    def project_exists(self, project_slug: str) -> bool:
        """Check if the project exists in the remote Transifex repository"""
        try:
            if self.get_project():
                return True
            return False
        except DoesNotExist:
            return False

    def create_project(self):
        source_language = tx_api.Language.get(code=self.config.source_language_code)
        project_name = self.config.project_name or self.config.project_slug

        if self.config.private:
            tx_api.Project.create(
                name=project_name,
                slug=self.config.project_slug,
                source_language=source_language,
                private=self.config.private,
                organization=self.get_organization(),
            )
        else:
            tx_api.Project.create(
                name=project_name,
                slug=self.config.project_slug,
                source_language=source_language,
                private=self.config.private,
                organization=self.get_organization(),
                repository_url=self.config.repository_url,
            )

        return self.get_project()

    def delete_project(self):
        project = self.get_project()
        if project:
            project.delete()

    def create_resource(self):
        resource = tx_api.Resource.create(
            project=self.get_project(),
            name=self.config.resource_slug,
            slug=self.config.resource_slug,
            i18n_format=tx_api.I18nFormat(id=self.config.i18n_type),
        )

        with open(self.config.resource_file_path, "r") as fh:
            content = fh.read()

        tx_api.ResourceStringsAsyncUpload.upload(content, resource=resource)
        logger.info(f"Resource created: {self.config.resource_slug}")

    def get_resource(self):
        resources = self.get_project().fetch("resources")
        if not resources:
            return None
        return resources.get(slug=self.config.resource_slug)

    def list_resources(self):
        if resources := self.get_project().fetch("resources"):
            return list(resources.all())
        else:
            return []

    def list_languages(self):
        languages = self.get_project().fetch("languages").all()
        return [lang.code for lang in languages]

    def create_language(self, language_code: str, coordinators):
        if language := tx_api.Language.get(code=language_code):
            logger.debug(f"Adding {language.code} to {self.config.project_slug}")
            self.get_project().add("languages", [language])

        # if coordinators:
        #    self.get_project().add("coordinators", coordinators)

    def update_source_translation(self):
        with open(self.config.resource_file_path, "r") as fh:
            content = fh.read()

        tx_api.ResourceStringsAsyncUpload.upload(content, resource=self.get_resource())
        logger.info(f"Source updated for resource: {self.config.resource_slug}")

    def get_translation(
        self,
        language_code: str,
        path_to_output_file: str,
    ) -> str:
        """Fetch the translation resource matching the given language"""
        path_to_parent = Path(path_to_output_file).parent

        Path.mkdir(path_to_parent, parents=True, exist_ok=True)
        language = tx_api.Language.get(code=language_code)

        url = tx_api.ResourceTranslationsAsyncDownload.download(
            resource=self.get_resource(), language=language
        )

        translated_content = requests.get(url).text
        with open(path_to_output_file, "w") as fh:
            fh.write(translated_content)

        logger.info(
            f"Translations downloaded and written to file (resource: {self.config.resource_slug})"
        )
        return str(path_to_output_file)
