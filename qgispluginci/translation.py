import glob
import subprocess
from pathlib import Path
from typing import Union

from pytransifex import Transifex

from qgispluginci.exceptions import (
    TransifexManyResources,
    TransifexNoResource,
    TranslationFailed,
)
from qgispluginci.parameters import Parameters
from qgispluginci.utils import touch_file


class Translation:
    def __init__(
        self,
        parameters: Parameters,
        source_translation: str = "transifex",
        # transifex specific
        transifex_token: str = None,
        transifex_create_project: bool = True,
    ):
        """Manage translation files for the plugin.

        Args:
            parameters (Parameters): CLI parameters
            source_translation (str, optional): source of translation to use. \
            Implemented: local or transifex. Defaults to "transifex".
            transifex_token (str, optional): Transifex API token. Defaults to None.
            transifex_create_project (bool, optional): if True, it will create the \
            project, resource and language on Transifex. Defaults to True.

        Raises:
            TranslationFailed: [description]
        """
        # store parameters as attributes
        self.parameters = parameters

        if source_translation == "transifex":
            self.transifex_create_project = transifex_create_project
            self._t = Transifex(
                api_token=transifex_token,
                organization=parameters.transifex_organization,
                i18n_type="QT",
            )
            assert self._t.ping()

        elif source_translation == "local":
            pass
        else:
            raise NotImplementedError("Source of translation not implemented")

    def process_translation_transifex(self):
        """Process translation using Transifex.

        Raises:
            TranslationFailed: if something went wrong
        """
        self.ts_file = "{dir}/i18n/{res}_{lan}.ts".format(
            dir=self.parameters.plugin_path,
            res=self.parameters.transifex_resource,
            lan=self.parameters.translation_source_language,
        )

        if self._t.project_exists(self.parameters.transifex_project):
            print(
                "Project {o}/{p} exists on Transifex".format(
                    o=self.parameters.transifex_organization,
                    p=self.parameters.transifex_project,
                )
            )
        elif self.transifex_create_project:
            print(
                "project does not exists on Transifex, creating one as {o}/{p}".format(
                    o=self.parameters.transifex_organization,
                    p=self.parameters.transifex_project,
                )
            )
            self._t.transifex_create_project(
                slug=self.parameters.transifex_project,
                repository_url=self.parameters.repository_url,
                source_language_code=self.parameters.translation_source_language,
            )
            self.update_strings()
            print(
                "creating resource in {o}/{p}/{r} with {f}".format(
                    o=self.parameters.transifex_organization,
                    p=self.parameters.transifex_project,
                    r=self.parameters.transifex_resource,
                    f=self.ts_file,
                )
            )
            self._t.create_resource(
                project_slug=self.parameters.transifex_project,
                path_to_file=self.ts_file,
                resource_slug=self.parameters.transifex_resource,
            )
            print("OK")
        else:
            raise TranslationFailed(
                "Project {o}/{p} does not exists on Transifex".format(
                    o=self.parameters.transifex_organization,
                    p=self.parameters.transifex_project,
                )
            )

    def process_translation_local(self):
        """Process the local translation files."""
        # check if there is a *.pro file
        project_file = self.get_qmake_project_file()
        if not project_file:
            project_file = self.create_qmake_project_file_on_fly()
            temp_pro_file = True
        else:
            temp_pro_file = False

        # update strings
        self.run_lupdate(project_file=project_file, verbose=True)
        self.run_lrelease()

        # clean up
        if temp_pro_file:
            project_file.unlink()

    def get_qmake_project_file(self) -> Union[Path, None]:
        """Look for a *.pro file in the plugin directory.

        Raises:
            Warning: if more than one *.pro file is found.

        Returns:
            Union[Path, None]: path to the *.pro file or None if not found.
        """
        plugin_folder_path = Path(self.parameters.plugin_path)
        qmake_project_files = sorted(list(plugin_folder_path.glob("**/*.pro")))

        if not len(qmake_project_files):
            print("No QMake project file (.pro) found.")
            return None
        elif len(qmake_project_files) == 1:
            print(f"QMake project file (.pro) found: {qmake_project_files[0]}")
            return qmake_project_files[0]
        else:
            raise Warning(
                "There are more than one QMake project file (.pro) file in the plugin "
                f"folder. The first will be used as fallback: {qmake_project_files[0]}"
            )

    def create_qmake_project_file_on_fly(self) -> Path:
        """Generate a QMake project file (*.pro) on the fly from forms (*.ui), \
        sources (*.py) and selected languages for translation (*.ts).

        Returns:
            Path: project file (*.pro) path
        """
        plugin_folder_path = Path(self.parameters.plugin_path)

        # listing relevant files in the plugin folder
        source_py_files = sorted(
            str(src.relative_to(plugin_folder_path))
            for src in plugin_folder_path.glob("**/*.py")
        )
        source_ui_files = sorted(
            str(src.relative_to(plugin_folder_path))
            for src in plugin_folder_path.glob("**/*.ui")
        )
        ts_files = sorted(
            str(src.relative_to(plugin_folder_path))
            for src in plugin_folder_path.glob("**/*.ts")
        )

        # if no ts_files, create empty files for select translations
        for lang in self.parameters.translation_languages:
            ts_file = f"{plugin_folder_path}/i18n/{self.parameters.transifex_resource}_{lang}.ts"
            print(ts_file)

        # write output project file
        project_file = plugin_folder_path / f"{self.parameters.plugin_slug}.pro"

        with project_file.open(mode="w", encoding="UTF8") as f:
            f.write("CODECFORTR = UTF-8\n\n")
            f.write("FORMS = {} \n\n".format(" ".join(source_ui_files)))
            f.write("SOURCES = {} \n\n".format(" ".join(source_py_files)))
            f.write("TRANSLATIONS = {}\n\n".format("\n".join(ts_files)))

        print(f"QMake project file temporarily created on the fly: {project_file}")
        return project_file

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

        # run (py)lupdate(5) path
        self.run_lupdate(project_file=project_file, drop_obsoletes=True)
        project_file.unlink()

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
            raise TranslationFailed(output.stderr)
        else:
            print("Successfully run lrelease: {}".format(output.stdout))

    # -- TRANSIFEX ---------------------------------------------------------------------
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
        print(
            "{c} languages found for resource "
            "{s}"
            " ({langs})".format(
                s=resource["slug"], c=len(existing_langs), langs=existing_langs
            )
        )
        for lang in self.parameters.translation_languages:
            if lang not in existing_langs:
                print("creating missing language: {}".format(lang))
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
            print("downloading translation file: {}".format(ts_file))
            self._t.get_translation(
                self.parameters.transifex_project, resource["slug"], lang, ts_file
            )

    def push(self):
        resource = self.__get_resource()
        print(
            "pushing resource: {} with file {}".format(
                self.parameters.transifex_resource, self.ts_file
            )
        )
        result = self._t.update_source_translation(
            project_slug=self.parameters.transifex_project,
            resource_slug=resource["slug"],
            path_to_file=self.ts_file,
        )
        print("done: {}".format(result))

    def __get_resource(self) -> dict:
        resources = self._t.list_resources(self.parameters.transifex_project)
        if len(resources) == 0:
            raise TransifexNoResource(
                "project '{}' has no resource on Transifex".format(
                    self.parameters.transifex_project
                )
            )
        if len(resources) > 1:
            for resource in resources:
                if resource["name"] == self.parameters.transifex_resource:
                    return resource
            raise TransifexManyResources(
                "project '{p}' has several resources on Transifex "
                "and none is named as the project slug."
                "Specify one in the parameters with transifex_resource."
                "These resources have been found: {r}".format(
                    p=self.parameters.transifex_project,
                    r=", ".join([r["name"] for r in resources]),
                )
            )
        return resources[0]

    # -- SUBPROCESSES ------------------------------------------------------------------
    def run_lrelease(self):
        """Execute the Qt Linguist release tool to compile TS file into QM files.

        Raises:
            subprocess.CalledProcessError: if the subprocess fails.
        """
        plugin_folder_path = Path(self.parameters.plugin_path)
        # cmd base
        cmd = [self.parameters.lrelease_path]

        # append translation files
        for ts in plugin_folder_path.glob("**/*.ts"):
            cmd.append(str(ts))

        print(f"Running Qt Linguist release command: {cmd}")
        output = subprocess.run(cmd, capture_output=True, text=True)

        if output.returncode != 0:
            raise subprocess.CalledProcessError(output.stderr)
        else:
            print(
                "Successfully run lrelease: {}".format(output.stdout or output.stderr)
            )

    def run_lupdate(
        self, project_file: Path, drop_obsoletes: bool = True, verbose: bool = False
    ):
        """Execute the Qt Linguist CLI defined in parameters (typically lupdate or \
        pylupdate5) to update *.ts files from a project file (.pro).

        Args:
            project_file (Path): QMake project file (*.pro)
            drop_obsoletes (bool, optional): add '-noobsolete' option to drop all \
            obsolete and vanished strings. Defaults to True.
            verbose (bool, optional): add verbose option. Defaults to False.

        Raises:
            subprocess.CalledProcessError: if the subprocess fails.
        """
        # cmd base
        cmd = [self.parameters.pylupdate5_path]

        # options
        if drop_obsoletes:
            cmd.append("-noobsolete")

        if verbose:
            cmd.append("-verbose")

        # add project file
        cmd.append(str(project_file))

        print(f"Running Qt Linguist update command: {cmd}")
        output = subprocess.run(cmd, capture_output=True, text=True)

        if output.returncode != 0:
            raise subprocess.CalledProcessError(output.stderr)
        else:
            print(
                "Successfully run pylupdate5: {}".format(output.stdout or output.stderr)
            )
