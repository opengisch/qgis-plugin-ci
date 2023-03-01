#!/usr/bin/python3

import logging
import os
import re
import sys
import tarfile
import xmlrpc.client
import zipfile
from glob import glob
from pathlib import Path
from tempfile import mkstemp

import git
from github import Github, GithubException

try:
    import importlib.resources as importlib_resources
except ImportError:
    # In Py<3.7 fall-back to backported `importlib_resources`.
    import importlib_resources

import datetime

import pyqt5ac

from qgispluginci.changelog import ChangelogParser
from qgispluginci.exceptions import (
    BuiltResourceInSources,
    GithubReleaseCouldNotUploadAsset,
    GithubReleaseNotFound,
    MissingChangelog,
    UncommitedChanges,
)
from qgispluginci.parameters import Parameters
from qgispluginci.translation import Translation
from qgispluginci.utils import (
    configure_file,
    convert_octets,
    parse_tag,
    replace_in_file,
)

# GLOBALS
logger = logging.getLogger(__name__)


def create_archive(
    parameters: Parameters,
    release_version: str,
    archive_name: str,
    add_translations: bool = False,
    allow_uncommitted_changes: bool = False,
    is_prerelease: bool = False,
    raise_min_version: str = None,
    disable_submodule_update: bool = False,
):
    repo = git.Repo()

    top_tar_handle, top_tar_file = mkstemp(suffix=".tar")

    # keep track of current state
    initial_stash = None
    diff = repo.index.diff(None)
    if diff:
        logger.info("There are uncommitted changes:")
        for diff in diff:
            logger.info(diff)
        if not allow_uncommitted_changes:
            err_msg = (
                "You have uncommitted changes. "
                "Stash or commit them or use -c / --allow-uncommitted-changes option."
            )
            logger.error(err_msg, exc_info=UncommitedChanges())
            sys.exit(1)
        else:
            initial_stash = repo.git.stash("create")

    # changelog
    if parameters.changelog_include:
        parser = ChangelogParser(
            parent_folder=Path(parameters.plugin_path).resolve().parent,
            changelog_path=parameters.changelog_path,
        )
        if parser.has_changelog():
            try:
                content = parser.last_items(
                    count=parameters.changelog_number_of_entries
                )
                if content:
                    replace_in_file(
                        "{}/metadata.txt".format(parameters.plugin_path),
                        r"^changelog=.*$",
                        "changelog={}".format(content),
                    )
            except Exception as exc:
                # Do not fail the release process if something is wrong when parsing the changelog
                replace_in_file(
                    "{}/metadata.txt".format(parameters.plugin_path),
                    r"^changelog=.*$",
                    "",
                )
                logger.warning(
                    f"An exception occurred while parsing the changelog file: {exc}",
                    exc_info=exc,
                )
    else:
        # Remove the changelog line
        replace_in_file(
            "{}/metadata.txt".format(parameters.plugin_path), r"^changelog=.*$", ""
        )

    # set version in metadata
    replace_in_file(
        "{}/metadata.txt".format(parameters.plugin_path),
        r"^version=.*$",
        "version={}".format(release_version),
    )

    # Commit number
    replace_in_file(
        f"{parameters.plugin_path}/metadata.txt",
        r"^commitNumber=.*$",
        f"commitNumber={len(list(repo.iter_commits()))}",
    )

    # Git SHA1
    replace_in_file(
        f"{parameters.plugin_path}/metadata.txt",
        r"^commitSha1=.*$",
        f"commitSha1={repo.head.object.hexsha}",
    )

    # Date/time in UTC
    date_time = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    replace_in_file(
        f"{parameters.plugin_path}/metadata.txt",
        r"^dateTime=.*$",
        f"dateTime={date_time}",
    )

    # set the plugin as experimental on a pre-release
    if is_prerelease:
        replace_in_file(
            "{}/metadata.txt".format(parameters.plugin_path),
            r"^experimental=.*$",
            "experimental={}".format(True if is_prerelease else False),
        )

    if raise_min_version:
        replace_in_file(
            "{}/metadata.txt".format(parameters.plugin_path),
            r"^qgisMinimumVersion=.*$",
            "qgisMinimumVersion={}".format(raise_min_version),
        )

    # replace any DEBUG=False in all Python files
    if not is_prerelease:
        for file in glob("{}/**/*.py".format(parameters.plugin_path), recursive=True):
            replace_in_file(file, r"^DEBUG\s*=\s*True", "DEBUG = False")

    # keep track of current state
    try:
        stash = repo.git.stash("create")
    except git.exc.GitCommandError:
        stash = "HEAD"
    if stash == "" or stash is None:
        stash = "HEAD"
    # create TAR archive
    logger.debug(f"Git archive plugin with stash: {stash}")
    repo.git.archive(stash, "-o", top_tar_file, parameters.plugin_path)
    # adding submodules
    for submodule in repo.submodules:
        _, sub_tar_file = mkstemp(suffix=".tar")
        if submodule.path.split("/")[0] != parameters.plugin_path:
            logger.debug(
                f"Skipping submodule not in plugin source directory: {submodule.name}"
            )
            continue
        if not disable_submodule_update:
            submodule.update(init=True)
        sub_repo = submodule.module()
        logger.info("Git archive submodule: {sub_repo}")
        sub_repo.git.archive(
            "HEAD", "--prefix", f"{submodule.path}/", "-o", sub_tar_file
        )
        with tarfile.open(top_tar_file, mode="a") as tt:
            with tarfile.open(sub_tar_file, mode="r:") as st:
                for m in st.getmembers():
                    if not m.isfile():
                        continue
                    tt.add(m.name)

    # add translation files
    if add_translations:
        with tarfile.open(top_tar_file, mode="a") as tt:
            logger.debug("Adding translations")
            for file in glob(f"{parameters.plugin_path}/i18n/*.qm"):
                logger.debug(f"  adding translation: {os.path.basename(file)}")
                # https://stackoverflow.com/a/48462950/1548052
                tt.add(file)

    # compile qrc files
    if list(Path(parameters.plugin_path).glob("*.qrc")):
        pyqt5ac.main(
            ioPaths=[
                [
                    f"{parameters.plugin_path}/*.qrc",
                    f"{parameters.plugin_path}/%%FILENAME%%_rc.py",
                ]
            ]
        )
        for file in glob(f"{parameters.plugin_path}/*_rc.py"):
            with tarfile.open(top_tar_file, mode="r:") as tt:
                for n in tt.getnames():
                    if n == file:
                        err_msg = (
                            f"The file {file} is present in the sources and its name "
                            "conflicts with a just built resource. "
                            "You might want to remove it from the sources or "
                            "setting export-ignore in .gitattributes config file."
                        )
                        logger.error(err_msg, exc_info=BuiltResourceInSources())
                        sys.exit(1)
            with tarfile.open(top_tar_file, mode="a") as tt:
                logger.debug(f"\tAdding resource: {file}")
                # https://stackoverflow.com/a/48462950/1548052
                tt.add(file)

    # converting to ZIP
    # why using TAR before? because it provides the prefix and makes things easier
    with zipfile.ZipFile(
        file=archive_name, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        # adding the content of TAR archive
        with tarfile.open(top_tar_file, mode="r:") as tt:
            for m in tt.getmembers():
                if m.isdir():
                    continue
                f = tt.extractfile(m)
                fl = f.read()
                fn = m.name
                # Get permissions and add it to ZipInfo
                st = os.stat(m.name)
                info = zipfile.ZipInfo(fn)

                # Using flags as defined in python zipfile module
                # code : https://github.com/python/cpython/blob/b885b8f4be9c74ef1ce7923dbf055c31e7f47735/Lib/zipfile.py#L545
                # see https://stackoverflow.com/questions/434641/how-do-i-set-permissions-attributes-on-a-file-in-a-zip-file-using-pythons-zip/53008127#53008127
                info.external_attr = (st[0] & 0xFFFF) << 16  # Unix attributes
                info.compress_type = zf.compression
                zf.writestr(info, fl)

    logger.debug("-" * 40)
    logger.debug(f"Files in ZIP archive ({archive_name}):")
    with zipfile.ZipFile(file=archive_name, mode="r") as zf:
        for f in zf.namelist():
            logger.debug(f)
    logger.debug("-" * 40)

    # checkout to reset changes
    if initial_stash:
        repo.git.reset("--hard", initial_stash)
        repo.git.reset("HEAD^")
    else:
        repo.git.checkout("--", ".")

    # print the result
    print(  # noqa: T2
        f"Plugin archive created: {archive_name} "
        f"({convert_octets(Path(archive_name).stat().st_size)})"
    )


def upload_asset_to_github_release(
    parameters: Parameters,
    asset_path: str,
    release_tag: str,
    github_token: str,
    asset_name: str = None,
):
    slug = f"{parameters.github_organization_slug}/{parameters.project_slug}"
    repo = Github(github_token).get_repo(slug)
    try:
        logger.debug(
            f"Getting release on {parameters.github_organization_slug}"
            f"/{parameters.project_slug}"
        )
        gh_release = repo.get_release(id=release_tag)
        logger.debug(
            f"Release retrieved from GitHub: {gh_release}, "
            f"{gh_release.tag_name}, "
            f"{gh_release.upload_url}"
        )
    except GithubException as exc:
        logger.error(
            f"Release {release_tag} not found for {slug}",
            exc_info=GithubReleaseNotFound(exc),
        )
        sys.exit(1)
    try:
        assert os.path.exists(asset_path)
        if asset_name:
            logger.debug(f"Uploading asset: {asset_path} as {asset_name}")

            uploaded_asset = gh_release.upload_asset(
                path=asset_path, label=asset_name, name=asset_name
            )
        else:
            logger.debug(f"Uploading asset: {asset_path}")
            uploaded_asset = gh_release.upload_asset(asset_path)
        logger.info(f"Asset successfully uploaded: {uploaded_asset.url}")
    except GithubException as exc:
        logger.error(
            f"Could not upload asset for release {release_tag} on {slug}. "
            "Are you sure the user for the given token can upload asset to this repo?",
            exc_info=GithubReleaseCouldNotUploadAsset(exc),
        )
        sys.exit(1)


def release_is_prerelease(
    parameters: Parameters,
    release_tag: str,
    github_token: str,
) -> bool:
    """Check the tag name or the GitHub release if the version must be experimental or not."""

    if parse_tag(release_tag).is_prerelease:
        # The tag itself is a pre-release according to https://semver.org/
        return True

    if not github_token:
        return False

    slug = f"{parameters.github_organization_slug}/{parameters.project_slug}"
    repo = Github(github_token).get_repo(slug)
    try:
        logger.debug(
            f"Getting release on {parameters.github_organization_slug}"
            f"/{parameters.project_slug}"
        )
        gh_release = repo.get_release(id=release_tag)
        logger.debug(
            f"Release retrieved from GitHub: {gh_release}, "
            f"{gh_release.tag_name}, "
            f"{gh_release.upload_url}"
        )
    except GithubException as exc:
        logger.error(
            f"Release {release_tag} not found. Trace: {exc}",
            exc_info=GithubReleaseNotFound(),
        )
        sys.exit(1)
    return gh_release.prerelease


def create_plugin_repo(
    parameters: Parameters,
    release_version: str,
    release_tag: str,
    archive: str,
    osgeo_username: str,
    is_prerelease: bool = False,
    plugin_repo_url: str = None,
) -> str:
    """
    Creates the plugin repo as an XML file
    """
    replace_dict = {
        "__RELEASE_VERSION__": release_version,
        "__RELEASE_TAG__": release_tag or release_version,
        "__PLUGIN_NAME__": parameters.plugin_name,
        "__RELEASE_DATE__": datetime.date.today().strftime("%Y-%m-%d"),
        "__CREATE_DATE__": parameters.create_date.strftime("%Y-%m-%d"),
        "__ORG__": parameters.github_organization_slug,
        "__REPO__": parameters.project_slug,
        "__PLUGINZIP__": archive,
        "__OSGEO_USERNAME__": osgeo_username or parameters.author,
        "__DEPRECATED__": str(parameters.deprecated),
        "__EXPERIMENTAL__": str(is_prerelease or parameters.experimental),
        "__TAGS__": parameters.tags,
        "__ICON__": parameters.icon,
        "__AUTHOR__": parameters.author,
        "__QGIS_MIN_VERSION__": parameters.qgis_minimum_version,
        "__DESCRIPTION__": parameters.description,
        "__ISSUE_TRACKER__": parameters.issue_tracker,
        "__HOMEPAGE__": parameters.homepage,
        "__REPO_URL__": parameters.repository_url,
    }
    if not plugin_repo_url:
        orgs = replace_dict["__ORG__"]
        repo = replace_dict["__REPO__"]
        tag = replace_dict["__RELEASE_TAG__"]
        plugin_zip = replace_dict["__PLUGINZIP__"]
        download_url = (
            f"https://github.com/{orgs}/{repo}/releases/download/{tag}/{plugin_zip}"
        )
        _, xml_repo = mkstemp(suffix=".xml")
    else:
        download_url = f"{plugin_repo_url}{replace_dict['__PLUGINZIP__']}"
        xml_repo = "./plugins.xml"
    replace_dict["__DOWNLOAD_URL__"] = download_url
    with importlib_resources.path(
        "qgispluginci", "plugins.xml.template"
    ) as xml_template:
        configure_file(xml_template, xml_repo, replace_dict)
    return xml_repo


def upload_plugin_to_osgeo(
    username: str, password: str, archive: str, server_url: str = None
):
    """
    Upload the plugin to QGIS repository

    Parameters
    ----------
    server_url
        The plugin server URL (defaults to plugins.qgis.org)
    username
        The username
    password
        The password
    archive
        The plugin archive file path to be uploaded
    """
    if not server_url:
        server_url = "plugins.qgis.org:443/plugins/RPC2/"
    address = f"https://{username}:{password}@{server_url}"

    server = xmlrpc.client.ServerProxy(
        address, verbose=(logger.getEffectiveLevel() <= 10)
    )

    try:
        logger.debug(f"Start uploading {archive} to QGIS plugins repository.")
        with open(archive, "rb") as handle:
            plugin_id, version_id = server.plugin.upload(
                xmlrpc.client.Binary(handle.read())
            )
        logger.debug(f"Plugin ID: {plugin_id}")
        logger.debug(f"Version ID: {version_id}")
    except xmlrpc.client.ProtocolError as err:
        url = re.sub(r":[^/].*@", ":******@", err.url)
        err_msg = (
            "=== A protocol error occurred ===\n"
            f"URL: {url}\n"
            f"HTTP/HTTPS headers: {err.headers}\n"
            f"Error code: {err.errcode}\n"
            f"Error message: {err.errmsg}\n"
            f"Plugin path: {archive}"
        )
        logger.error(err_msg)
        sys.exit(err_msg)
    except xmlrpc.client.Fault as err:
        err_msg = (
            "=== A fault occurred occurred ===\n"
            f"Fault code: {err.faultCode}\n"
            f"Fault string: {err.faultString}\n"
            f"Plugin path: {archive}"
        )
        logger.error(err_msg)
        sys.exit(err_msg)


def release(
    parameters: Parameters,
    release_version: str,
    release_tag: str = None,
    github_token: str = None,
    upload_plugin_repo_github: bool = False,
    tx_api_token: str = None,
    alternative_repo_url: str = None,
    osgeo_username: str = None,
    osgeo_password: str = None,
    allow_uncommitted_changes: bool = False,
    plugin_repo_url: str = None,
    disable_submodule_update: bool = False,
):
    """

    Parameters
    ----------
    parameters
        The configuration parameters
    release_version:
        The release version (x.y.z)
    release_tag:
        The release tag (vx.y.z).
        If not given, the release version will be used
    github_token
        The Github token
    upload_plugin_repo_github
        If true, a custom repo will be created as a release asset on Github and could later be used in QGIS as a custom plugin repository.
    plugin_repo_url
        If set, this URL will be used to create the ZIP URL in the XML file
    tx_api_token
        The Transifex token
    alternative_repo_url
        URL of the endpoint to upload the plugin to
    osgeo_username
        osgeo username to upload the plugin to official QGIS repository
    osgeo_password
        osgeo password to upload the plugin to official QGIS repository
    allow_uncommitted_changes
        If False, uncommitted changes are not allowed before packaging/releasing.
        If True and some changes are detected, a hard reset on a stash create will be used to revert changes made by qgis-plugin-ci.
    disable_submodule_update
        If omitted, a git submodule is updated. If specified, git submodules will not be updated/initialized before packaging.
    """

    if release_version == "latest":
        parser = ChangelogParser(
            parent_folder=Path(parameters.plugin_path).resolve().parent,
            changelog_path=parameters.changelog_path,
        )
        if parser.has_changelog():
            release_version = parser.latest_version()
        else:
            release_version = "latest"

    release_tag = release_tag or release_version

    if tx_api_token is not None:
        tr = Translation(parameters, create_project=False, tx_api_token=tx_api_token)
        tr.pull()
        tr.compile_strings()

    archive_name = parameters.archive_name(parameters.plugin_path, release_version)

    # check if the GitHub release is a regular or pre-release
    is_prerelease = release_is_prerelease(
        parameters, release_tag=release_tag, github_token=github_token
    )

    if is_prerelease:
        logger.info(f"{release_tag} is a pre-release.")
    else:
        logger.info(f"{release_tag} is a regular release.")

    create_archive(
        parameters,
        release_version,
        archive_name,
        add_translations=tx_api_token is not None,
        allow_uncommitted_changes=allow_uncommitted_changes,
        is_prerelease=is_prerelease,
        disable_submodule_update=disable_submodule_update,
    )

    # if pushing to QGIS repo and pre-release, create an extra package with qgisMinVersion to 3.14
    # since only QGIS 3.14+ supports the beta/experimental plugins trial
    experimental_archive_name = None
    if osgeo_username is not None and is_prerelease:
        experimental_archive_name = parameters.archive_name(
            parameters.plugin_path, release_version, True
        )
        create_archive(
            parameters,
            release_version,
            experimental_archive_name,
            add_translations=tx_api_token is not None,
            allow_uncommitted_changes=allow_uncommitted_changes,
            is_prerelease=True,
            raise_min_version="3.14",
            disable_submodule_update=disable_submodule_update,
        )

    if github_token is not None:
        upload_asset_to_github_release(
            parameters,
            asset_path=archive_name,
            release_tag=release_tag,
            github_token=github_token,
        )
        if upload_plugin_repo_github:
            xml_repo = create_plugin_repo(
                parameters=parameters,
                release_version=release_version,
                release_tag=release_tag,
                is_prerelease=is_prerelease,
                archive=archive_name,
                osgeo_username=osgeo_username,
            )
            upload_asset_to_github_release(
                parameters,
                asset_path=xml_repo,
                release_tag=release_tag,
                github_token=github_token,
                asset_name="plugins.xml",
            )

    if plugin_repo_url:
        xml_repo = create_plugin_repo(
            parameters=parameters,
            release_version=release_version,
            release_tag=release_tag,
            archive=archive_name,
            is_prerelease=is_prerelease,
            osgeo_username=osgeo_username,
            plugin_repo_url=plugin_repo_url,
        )
        logger.info(f"Local XML repo file created : {xml_repo}")

    if osgeo_username is not None:
        assert osgeo_password is not None
        if is_prerelease:
            assert experimental_archive_name is not None
            upload_plugin_to_osgeo(
                username=osgeo_username,
                password=osgeo_password,
                archive=experimental_archive_name,
                server_url=alternative_repo_url,
            )
        else:
            upload_plugin_to_osgeo(
                username=osgeo_username,
                password=osgeo_password,
                archive=archive_name,
                server_url=alternative_repo_url,
            )
