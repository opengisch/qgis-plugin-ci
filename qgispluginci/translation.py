import glob
import logging
import subprocess
import sys
from pathlib import Path

from pytransifex import Transifex

from qgispluginci.exceptions import (
    TransifexManyResources,
    TransifexNoResource,
    TranslationFailed,
)
from qgispluginci.parameters import Parameters
from qgispluginci.utils import touch_file

# GLOBALS
logger = logging.getLogger(__name__)


class Translation:
    def __init__(
        self, parameters: Parameters, transifex_token: str, create_project: bool = True
    ):
        """
        Parameters
        ----------
        parameters:

        transifex_token:
            Transifex API token

        create_project:
            if True, it will create the project, resource and language on Transifex

        """
        self.parameters = parameters
        self._t = Transifex(
            transifex_token, parameters.transifex_organization, i18n_type="QT"
        )
        assert self._t.ping()
        self.ts_file = "{dir}/i18n/{res}_{lan}.ts".format(
            dir=self.parameters.plugin_path,
            res=self.parameters.transifex_resource,
            lan=self.parameters.translation_source_language,
        )

        if self._t.project_exists(parameters.transifex_project):
            logger.debug(
                f"Project {self.parameters.transifex_organization}/"
                f"{self.parameters.transifex_project} exists on Transifex"
            )

        elif create_project:
            logger.debug(
                "Project does not exists on Transifex, creating one as: "
                f"{self.parameters.transifex_organization}/"
                f"{self.parameters.transifex_project}"
            )
            self._t.create_project(
                slug=self.parameters.transifex_project,
                repository_url=self.parameters.repository_url,
                source_language_code=parameters.translation_source_language,
            )
            self.update_strings()
            logger.debug(
                f"Creating resource in {self.parameters.transifex_organization}/"
                f"{self.parameters.transifex_project}/"
                f"{self.parameters.transifex_resource} with {self.ts_file}"
            )
            self._t.create_resource(
                project_slug=self.parameters.transifex_project,
                path_to_file=self.ts_file,
                resource_slug=self.parameters.transifex_resource,
            )
            logger.info(
                "Transifex project {self.parameters.transifex_organization}/"
                f"{self.parameters.transifex_project} and resource have been created."
            )
        else:
            logger.error(
                "Project does not exists on Transifex: "
                f"{self.parameters.transifex_organization}/"
                f"{self.parameters.transifex_project}",
                exc_info=TranslationFailed(),
            )

    def update_strings(self):
        """
        Update TS files from plugin source strings
        """
        source_py_files = []
        source_ui_files = []
        relative_path = "./{plugin_path}".format(
            plugin_path=self.parameters.plugin_path
        )
        for ext in ("py", "ui"):
            for file in glob.glob(
                "{dir}/**/*.{ext}".format(dir=self.parameters.plugin_path, ext=ext),
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
            assert f.write("CODECFORTR = UTF-8\n")
            assert f.write("SOURCES = {}\n".format(" ".join(source_py_files)))
            assert f.write("FORMS = {}\n".format(" ".join(source_ui_files)))
            assert f.write(
                "TRANSLATIONS = {}\n".format(
                    Path(self.ts_file).relative_to(relative_path)
                )
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
        for file in glob.glob(
            "{dir}/i18n/*.ts".format(dir=self.parameters.plugin_path)
        ):
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
        resource = self.__get_resource()
        existing_langs = self._t.list_languages(
            project_slug=self.parameters.transifex_project,
            resource_slug=resource["slug"],
        )
        existing_langs.remove(self.parameters.translation_source_language)
        logger.info(
            f"{len(existing_langs)} languages found for resource {resource.get('slug')}:"
            f" ({existing_langs})"
        )
        for lang in self.parameters.translation_languages:
            if lang not in existing_langs:
                logger.debug(f"Creating missing language: {lang}")
                self._t.create_language(
                    self.parameters.transifex_project,
                    lang,
                    [self.parameters.transifex_coordinator],
                )
                existing_langs.append(lang)
        for lang in existing_langs:
            ts_file = "{dir}/i18n/{res}_{lan}.ts".format(
                dir=self.parameters.plugin_path,
                res=self.parameters.transifex_resource,
                lan=lang,
            )
            logger.debug(f"Downloading translation file: {ts_file}")
            self._t.get_translation(
                self.parameters.transifex_project, resource["slug"], lang, ts_file
            )

    def push(self):
        resource = self.__get_resource()
        logger.debug(
            f"Pushing resource: {self.parameters.transifex_resource} "
            f"with file {self.ts_file}"
        )
        result = self._t.update_source_translation(
            project_slug=self.parameters.transifex_project,
            resource_slug=resource["slug"],
            path_to_file=self.ts_file,
        )
        logger.info(f"Translation resource updated: {result}")

    def __get_resource(self) -> dict:
        resources = self._t.list_resources(self.parameters.transifex_project)
        if len(resources) == 0:
            logger.error(
                f"Project '{self.parameters.transifex_project}' has no resource on Transifex",
                exc_info=TransifexNoResource(),
            )
            sys.exit(1)
        if len(resources) > 1:
            for resource in resources:
                if resource["name"] == self.parameters.transifex_resource:
                    return resource
            logger.error(
                f"Project '{self.parameters.transifex_project}' has several "
                "resources on Transifex and none is named as the project slug. "
                "Specify one in the parameters with transifex_resource."
                "These resources have been found: "
                f"{', '.join([r['name'] for r in resources])}",
                exc_info=TransifexManyResources(),
            )
            sys.exit(1)
        return resources[0]
