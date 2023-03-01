import glob
import logging
import subprocess
import sys
from pathlib import Path

from qgispluginci.exceptions import (
    TransifexManyResources,
    TransifexNoResource,
    TranslationFailed,
)
from qgispluginci.parameters import Parameters
from qgispluginci.translation_clients.baseclient import TranslationConfig
from qgispluginci.translation_clients.transifex import TransifexClient
from qgispluginci.utils import touch_file

# GLOBALS
logger = logging.getLogger(__name__)


class Translation:
    def __init__(
        self, parameters: Parameters, tx_api_token: str, create_project: bool = True
    ):
        """
        Parameters
        ----------
        parameters:

        tx_api_token:
            Transifex API token

        create_project:
            if True, it will create the project, resource and language on Transifex

        """
        self.parameters = parameters

        plugin_path = self.parameters.plugin_path
        tx = self.parameters.transifex_resource
        lang = self.parameters.translation_source_language
        self.ts_file = f"{plugin_path}/i18n/{tx}_{lang}.ts"

        tx_config = TranslationConfig(
            api_token=tx_api_token,
            organization_name=parameters.transifex_organization,
            project_slug=parameters.transifex_project,
            repository_url=parameters.repository_url,
            source_language_code=parameters.translation_source_language,
            resource_file_path=self.ts_file,
            resource_slug=self.parameters.transifex_resource,
        )
        self.tx_client = TransifexClient(tx_config, self.update_strings, create_project)

    def update_strings(self):
        """
        Update TS files from plugin source strings
        """
        source_py_files = []
        source_ui_files = []
        relative_path = f"./{self.parameters.plugin_path}"
        for ext in ("py", "ui"):
            for file in glob.glob(
                f"{self.parameters.plugin_path}/**/*.{ext}",
                recursive=True,
            ):
                file_path = str(Path(file).relative_to(relative_path))
                if ext == "py":
                    source_py_files.append(file_path)
                else:
                    source_ui_files.append(file_path)

        touch_file(self.ts_file)

        project_file = Path(self.parameters.plugin_path).joinpath(
            self.parameters.plugin_name + ".pro"
        )

        with open(project_file, "w") as f:
            source_py_files = " ".join(source_py_files)
            source_ui_files = " ".join(source_ui_files)
            assert f.write("CODECFORTR = UTF-8\n")
            assert f.write(f"SOURCES = {source_py_files}\n")
            assert f.write(f"FORMS = {source_ui_files}\n")
            assert f.write(
                f"TRANSLATIONS = {Path(self.ts_file).relative_to(relative_path)}\n"
            )
            f.flush()
            f.close()

        cmd = [self.parameters.pylupdate5_path, "-noobsolete", str(project_file)]

        output = subprocess.run(cmd, capture_output=True, text=True)

        project_file.unlink()

        if output.returncode != 0:
            logger.error(
                f"Translation failed: {output.stderr}", exc_info=TranslationFailed()
            )
            sys.exit(1)
        else:
            logger.info(f"Successfully run pylupdate5: {output.stdout}")

    def compile_strings(self):
        """
        Compile TS file into QM files
        """
        cmd = [self.parameters.lrelease_path]
        for file in glob.glob(f"{self.parameters.plugin_path}/i18n/*.ts"):
            cmd.append(file)
        output = subprocess.run(cmd, capture_output=True, text=True)
        if output.returncode != 0:
            logger.error(
                f"Translation failed: {output.stderr}", exc_info=TranslationFailed()
            )
            sys.exit(1)
        else:
            logger.info(f"Successfully run lrelease: {output.stdout}")

    def pull(self):
        """
        Pull TS files from Transifex
        """
        resource = self.tx_client.get_resource()
        existing_langs = self.tx_client.list_languages()
        logger.info(
            f"{len(existing_langs)} languages found for resource {resource}:"
            f" ({existing_langs})"
        )
        for lang in self.parameters.translation_languages:
            if lang not in existing_langs:
                logger.debug(f"Creating missing language: {lang}")
                self.tx_client.create_language(
                    language_code=lang,
                    coordinators=[self.parameters.transifex_coordinator],
                )
                existing_langs.append(lang)
        for lang in existing_langs:
            ts_file = f"{self.parameters.plugin_path}/i18n/{self.parameters.transifex_resource}_{lang}.ts"
            logger.debug(f"Downloading translation file: {ts_file}")
            self.tx_client.get_translation(
                language_code=lang,
                path_to_output_file=ts_file,
            )

    def push(self):
        resource = self.tx_client.get_resource()
        logger.debug(
            f"Pushing resource: {self.parameters.transifex_resource} "
            f"with file {self.ts_file}"
        )
        self.tx_client.update_source_translation()
