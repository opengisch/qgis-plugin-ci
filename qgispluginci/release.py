#!/usr/bin/python3

import os
import sys
import git
import tarfile
import zipfile
from tempfile import mkstemp
from glob import glob
from github import Github, GithubException
import xmlrpc.client
import re
import warnings

try:
  import importlib.resources as importlib_resources
except ImportError:
  # In Py<3.7 fall-back to backported `importlib_resources`.
  import importlib_resources
import datetime
import pyqt5ac

from qgispluginci.changelog import ChangelogParser
from qgispluginci.parameters import Parameters
from qgispluginci.translation import Translation
from qgispluginci.utils import replace_in_file, configure_file
from qgispluginci.exceptions import GithubReleaseNotFound, GithubReleaseCouldNotUploadAsset, UncommitedChanges


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

    top_tar_handle, top_tar_file = mkstemp(suffix='.tar')

    # keep track of current state
    initial_stash = None
    diff = repo.index.diff(None)
    if diff:
        print("Uncommitted changes:")
        for diff in diff:
            print(diff)
        if not allow_uncommitted_changes:
            raise UncommitedChanges('You have uncommitted changes. Stash or commit them or use --allow-uncommitted-changes.')
        else:
            initial_stash = repo.git.stash('create')

    # changelog
    if parameters.changelog_include:
        parser = ChangelogParser(parameters.changelog_regexp)
        if parser.has_changelog():
            try:
                content = parser.last_items(parameters.changelog_number_of_entries)
                if content:
                    replace_in_file(
                        '{}/metadata.txt'.format(parameters.plugin_path),
                        r'^changelog=.*$',
                        'changelog={}'.format(content)
                    )
            except Exception as e:
                # Do not fail the release process if something is wrong when parsing the changelog
                replace_in_file(
                    '{}/metadata.txt'.format(parameters.plugin_path),
                    r'^changelog=.*$', ''
                )
                print('An exception occurred while parsing the changelog file : {}'.format(e))
    else:
        # Remove the changelog line
        replace_in_file(
            '{}/metadata.txt'.format(parameters.plugin_path),
            r'^changelog=.*$', ''
        )

    # set version in metadata
    replace_in_file(
        '{}/metadata.txt'.format(parameters.plugin_path),
        r'^version=.*$',
        'version={}'.format(release_version)
    )

    # set the plugin as experimental on a pre-release
    if is_prerelease:
        replace_in_file(
            '{}/metadata.txt'.format(parameters.plugin_path),
            r'^experimental=.*$',
            'experimental={}'.format(True if is_prerelease else False)
        )

    if raise_min_version:
        replace_in_file(
            '{}/metadata.txt'.format(parameters.plugin_path),
            r'^qgisMinimumVersion=.*$',
            'qgisMinimumVersion={}'.format(raise_min_version)
        )

    # replace any DEBUG=False in all Python files
    if not is_prerelease:
        for file in glob('{}/**/*.py'.format(parameters.plugin_path), recursive=True):
            replace_in_file(file, r'^DEBUG\s*=\s*True', 'DEBUG = False')

    # keep track of current state
    try:
        stash = repo.git.stash('create')
    except git.exc.GitCommandError:
        stash = 'HEAD'
    if stash == '' or stash is None:
        stash = 'HEAD'
    # create TAR archive
    print('archive plugin with stash: {}'.format(stash))
    repo.git.archive(stash, '-o', top_tar_file, parameters.plugin_path)
    # adding submodules
    for submodule in repo.submodules:
        _, sub_tar_file = mkstemp(suffix='.tar')
        if submodule.path.split('/')[0] != parameters.plugin_path:
            print('skipping submodule not in plugin source directory ({})'.format(submodule.name))
            continue
        if not disable_submodule_update:
            submodule.update(init=True)
        sub_repo = submodule.module()
        print('archive submodule:', sub_repo)
        sub_repo.git.archive('HEAD', '--prefix', '{}/'.format(submodule.path), '-o', sub_tar_file)
        with tarfile.open(top_tar_file, mode="a") as tt:
            with tarfile.open(sub_tar_file, mode="r:") as st:
                for m in st.getmembers():
                    # print('adding', m, m.type, m.isfile())
                    if not m.isfile():
                        continue
                    tt.add(m.name)

    # add translation files
    if add_translations:
        with tarfile.open(top_tar_file, mode="a") as tt:
            print("adding translations")
            for file in glob('{}/i18n/*.qm'.format(parameters.plugin_path)):
                print('  adding translation: {}'.format(os.path.basename(file)))
                # https://stackoverflow.com/a/48462950/1548052
                tt.add(file)

    # compile qrc files
    pyqt5ac.main(ioPaths=[
        ['{}/*.qrc'.format(parameters.plugin_path), '{}/%%FILENAME%%_rc.py'.format(parameters.plugin_path)]
    ])
    for file in glob('{}/*_rc.py'.format(parameters.plugin_path)):
        with tarfile.open(top_tar_file, mode="a") as tt:
            print('  adding resource: {}'.format(file))
            # https://stackoverflow.com/a/48462950/1548052
            tt.add(file)

    # converting to ZIP
    # why using TAR before? because it provides the prefix and makes things easier
    with zipfile.ZipFile(file=archive_name, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        # adding the content of TAR archive
        with tarfile.open(top_tar_file, mode='r:') as tt:
            for m in tt.getmembers():
                if m.isdir():
                    continue
                f = tt.extractfile(m)
                fl = f.read()
                fn = m.name
                zf.writestr(fn, fl)

    print('-------')
    print('files in ZIP archive ({}):'.format(archive_name))
    with zipfile.ZipFile(file=archive_name, mode='r') as zf:
        for f in zf.namelist():
            print(f)
    print('-------')

    # checkout to reset changes
    if initial_stash:
        repo.git.reset('--hard', initial_stash)
        repo.git.reset('HEAD^')
    else:
        repo.git.checkout('--', '.')


def upload_asset_to_github_release(
        parameters: Parameters,
        asset_path: str,
        release_tag: str,
        github_token: str,
        asset_name: str = None
):

    slug = '{}/{}'.format(parameters.github_organization_slug, parameters.project_slug)
    repo = Github(github_token).get_repo(slug)
    try:
        print('Getting release on {}/{}'.format(parameters.github_organization_slug, parameters.project_slug))
        gh_release = repo.get_release(id=release_tag)
        print(gh_release, gh_release.tag_name, gh_release.upload_url)
    except GithubException as e:
        raise GithubReleaseNotFound('Release {} not found'.format(release_tag))
    try:
        assert os.path.exists(asset_path)
        if asset_name:
            print('Uploading asset: {} as {}'.format(asset_path, asset_name))
            gh_release.upload_asset(path=asset_path, label=asset_name, name=asset_name)
        else:
            print('Uploading asset: {}'.format(asset_path))
            gh_release.upload_asset(asset_path)
        print('OK')
    except GithubException as e:
        print(e)
        raise GithubReleaseCouldNotUploadAsset(
            'Could not upload asset for release {}. '
            'Are you sure the user for the given token can upload asset to this repo?'.format(release_tag)
        )


def release_is_prerelease(
        parameters: Parameters,
        release_tag: str,
        github_token: str,
) -> bool:
    slug = '{}/{}'.format(parameters.github_organization_slug, parameters.project_slug)
    repo = Github(github_token).get_repo(slug)
    try:
        print('Getting release on {}/{}'.format(parameters.github_organization_slug, parameters.project_slug))
        gh_release = repo.get_release(id=release_tag)
        print(gh_release, gh_release.tag_name, gh_release.upload_url)
    except GithubException as e:
        raise GithubReleaseNotFound('Release {} not found'.format(release_tag))
    return gh_release.prerelease


def create_plugin_repo(
        parameters: Parameters,
        release_version: str,
        release_tag: str,
        archive: str,
        osgeo_username,
        plugin_repo_url=None,
) -> str:
    """
    Creates the plugin repo as an XML file
    """
    replace_dict = {
        '__RELEASE_VERSION__': release_version,
        '__RELEASE_TAG__': release_tag or release_version,
        '__PLUGIN_NAME__': parameters.plugin_name,
        '__RELEASE_DATE__': datetime.date.today().strftime('%Y-%m-%d'),
        '__CREATE_DATE__': parameters.create_date.strftime('%Y-%m-%d'),
        '__ORG__': parameters.github_organization_slug,
        '__REPO__': parameters.project_slug,
        '__PLUGINZIP__': archive,
        '__OSGEO_USERNAME__': osgeo_username or parameters.author,
        '__DEPRECATED__': str(parameters.deprecated),
        '__EXPERIMENTAL__': str(parameters.experimental),
        '__TAGS__': parameters.tags,
        '__ICON__': parameters.icon,
        '__AUTHOR__': parameters.author,
        '__QGIS_MIN_VERSION__': parameters.qgis_minimum_version,
        '__DESCRIPTION__': parameters.description,
        '__ISSUE_TRACKER__': parameters.issue_tracker,
        '__HOMEPAGE__': parameters.homepage,
        '__REPO_URL__': parameters.repository_url
    }
    if not plugin_repo_url:
        download_url = 'https://github.com/{org}/{repo}/releases/download/{tag}/{pluginzip}'.format(
            org=replace_dict['__ORG__'],
            repo=replace_dict['__REPO__'],
            tag=replace_dict['__RELEASE_TAG__'],
            pluginzip=replace_dict['__PLUGINZIP__'],
        )
        _, xml_repo = mkstemp(suffix='.xml')
    else:
        download_url = '{url}{pluginzip}'.format(
            url=plugin_repo_url,
            pluginzip=replace_dict['__PLUGINZIP__'],
        )
        xml_repo = './plugins.xml'
    replace_dict['__DOWNLOAD_URL__'] = download_url
    with importlib_resources.path('qgispluginci', 'plugins.xml.template') as xml_template:
        configure_file(xml_template, xml_repo, replace_dict)
    return xml_repo


def upload_plugin_to_osgeo(username: str, password: str, archive: str):
    """
    Upload the plugin to QGIS repository

    Parameters
    ----------
    username
        The username
    password
        The password
    archive
        The plugin archive file path to be uploaded
    """
    address = "https://{username}:{password}@plugins.qgis.org:443/plugins/RPC2/".format(
        username=username,
        password=password)

    server = xmlrpc.client.ServerProxy(address, verbose=False)

    try:
        with open(archive, 'rb') as handle:
            plugin_id, version_id = server.plugin.upload(
                xmlrpc.client.Binary(handle.read()))
        print("Plugin ID: %s" % plugin_id)
        print("Version ID: %s" % version_id)
    except xmlrpc.client.ProtocolError as err:
        print("A protocol error occurred")
        print("URL: %s" % re.sub(r':[^/].*@', ':******@', err.url))
        print("HTTP/HTTPS headers: %s" % err.headers)
        print("Error code: %d" % err.errcode)
        print("Error message: %s" % err.errmsg)
        sys.exit(1)
    except xmlrpc.client.Fault as err:
        print("A fault occurred")
        print("Fault code: %d" % err.faultCode)
        print("Fault string: %s" % err.faultString)
        sys.exit(1)


def release(parameters: Parameters,
            release_version: str,
            release_tag: str = None,
            github_token: str = None,
            upload_plugin_repo_github: str = False,
            transifex_token: str = None,
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
    transifex_token
        The Transifex token
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

    if transifex_token is not None:
        tr = Translation(parameters, create_project=False, transifex_token=transifex_token)
        tr.pull()
        tr.compile_strings()

    archive_name = parameters.archive_name(release_version)

    is_prerelease = False
    if github_token is not None:
        is_prerelease = release_is_prerelease(parameters, release_tag=release_version, github_token=github_token)
    print("*** is pre-release: {}".format("YES" if is_prerelease else "NO"))

    create_archive(
        parameters, release_version, archive_name,
        add_translations=transifex_token is not None,
        allow_uncommitted_changes=allow_uncommitted_changes,
        is_prerelease=is_prerelease,
        disable_submodule_update=disable_submodule_update,
    )

    # if pushing to QGIS repo and pre-release, create an extra package with qgisMinVersion to 3.14
    # since only QGIS 3.14+ supports the beta/experimental plugins trial
    experimental_archive_name = None
    if osgeo_username is not None and is_prerelease:
        experimental_archive_name = parameters.archive_name(release_version, True)
        create_archive(
            parameters, release_version, experimental_archive_name,
            add_translations=transifex_token is not None,
            allow_uncommitted_changes=allow_uncommitted_changes,
            is_prerelease=True,
            raise_min_version='3.14',
            disable_submodule_update=disable_submodule_update,
        )

    if github_token is not None:
        upload_asset_to_github_release(
            parameters, asset_path=archive_name, release_tag=release_version, github_token=github_token
        )
        if upload_plugin_repo_github:
            xml_repo = create_plugin_repo(
                parameters=parameters,
                release_version=release_version,
                release_tag=release_tag,
                archive=archive_name,
                osgeo_username=osgeo_username
            )
            upload_asset_to_github_release(
                parameters,
                asset_path=xml_repo,
                release_tag=release_version,
                github_token=github_token,
                asset_name='plugins.xml'
            )

    if plugin_repo_url:
        xml_repo = create_plugin_repo(
            parameters=parameters,
            release_version=release_version,
            release_tag=release_tag,
            archive=archive_name,
            osgeo_username=osgeo_username,
            plugin_repo_url=plugin_repo_url,
        )
        print('Local XML repo file created : {}'.format(xml_repo))

    if osgeo_username is not None:
        assert osgeo_password is not None
        if is_prerelease:
            assert experimental_archive_name is not None
            upload_plugin_to_osgeo(username=osgeo_username, password=osgeo_password, archive=experimental_archive_name)
        else:
            upload_plugin_to_osgeo(username=osgeo_username, password=osgeo_password, archive=archive_name)
