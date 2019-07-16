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
import pkg_resources

from qgispluginci.parameters import Parameters
from qgispluginci.translation import Translation
from qgispluginci.utils import replace_in_file, configure_file
from qgispluginci.exceptions import GithubReleaseNotFound, GithubReleaseCouldNotUploadAsset


def release(parameters: Parameters,
            release_version: str,
            github_token: str = None,
            upload_plugin_repo_github: str = False,
            transifex_token: str = None,
            osgeo_username: str = None,
            osgeo_password: str = None):

    # set version in metadata
    replace_in_file('{}/metadata.txt'.format(parameters.src_dir),
                    r'^version=.*\$',
                    'version=${}'.format(release_version))

    # replace any DEBUG=False in the plugin main file
    replace_in_file('{d}/{f}'.format(d=parameters.src_dir, f=parameters.plugin_main_file),
                    r'^DEBUG\s*=\s*True',
                    'DEBUG = False')

    if transifex_token is not None:
        tr = Translation(parameters, create_project=False, transifex_token=transifex_token)
        tr.pull()
        tr.compile_strings()

    output = '{project_slug}-{release_version}.zip'.format(project_slug=parameters.project_slug,
                                                           release_version=release_version)
    create_archive(parameters, output=output, add_translations=transifex_token is not None)
    if github_token is not None:
        upload_asset_to_github_release(parameters, archive=output, release_tag=release_version, github_token=github_token)
        if upload_plugin_repo_github:
            xml_repo = create_plugin_repo()

    if osgeo_username is not None:
        assert osgeo_password is not None
        upload_plugin_to_osgeo(username=osgeo_username, password=osgeo_password, archive=output)


def create_archive(parameters: Parameters,
                   output: str,
                   add_translations: bool = False):
    top_tar_handle, top_tar_file = mkstemp(suffix='.tar')

    repo = git.Repo()
    try:
        stash = repo.git.stash('create')
    except git.exc.GitCommandError:
        stash = 'HEAD'
    if stash == '' or stash is None:
        stash = 'HEAD'
    # create TAR archive
    print('archive plugin with stash: {}'.format(stash))
    repo.git.archive(stash, '--prefix', '{}/'.format(parameters.src_dir), '-o', top_tar_file, parameters.src_dir)
    with tarfile.open(top_tar_file, mode="a") as tt:
        # adding submodules
        for submodule in repo.submodules:
            _, sub_tar_file = mkstemp(suffix='.tar')
            if submodule.path.split('/')[0] != parameters.src_dir:
                print('skipping submodule not in plugin source directory ({})'.format(submodule.name))
                continue
            submodule.update(init=True)
            sub_repo = submodule.module()
            print('archive submodule:', sub_repo)
            sub_repo.git.archive('HEAD', '--prefix', '{}/'.format(submodule.path), '-o', sub_tar_file)
            with tarfile.open(sub_tar_file, mode="r:") as st:
                for m in st.getmembers():
                    # print('adding', m, m.type, m.isfile())
                    if not m.isfile():
                        continue
                    tt.add(m.name, arcname='{}/{}'.format(parameters.src_dir, m.name))

        # add translation files
        if add_translations:
            print("adding translations")
            for file in glob('{}/i18n/*.qm'.format(parameters.src_dir)):
                print('  {}'.format(os.path.basename(file)))
                tt.addfile(tarfile.TarInfo('{s}/{s}/i18n/{f}'.format(s=parameters.src_dir, f=os.path.basename(file))), file)

    # converting to ZIP
    # why using TAR before? because it provides the prefix and makes things easier
    with zipfile.ZipFile(file=output, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
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
    print('files in ZIP archive:')
    with zipfile.ZipFile(file=output, mode='r') as zf:
        for f in zf.namelist():
            print(f)
    print('-------')


def upload_asset_to_github_release(parameters: Parameters,
                                   archive: str,
                                   release_tag: str,
                                   github_token: str):

    slug = '{}/{}'.format(parameters.organization_slug, parameters.project_slug)
    repo = Github(github_token).get_repo(slug)
    try:
        print('Getting release on {}/{}'.format(parameters.organization_slug, parameters.project_slug))
        gh_release = repo.get_release(id=release_tag)
        print(gh_release, gh_release.tag_name, gh_release.upload_url)
    except GithubException as e:
        raise GithubReleaseNotFound('Release {} not found'.format(release_tag))
    try:
        print('Uploading archive {}'.format(archive))
        assert os.path.exists(archive)
        gh_release.upload_asset(archive)
        print('OK')
    except GithubException as e:
        print(e)
        raise GithubReleaseCouldNotUploadAsset('Could not upload asset for release {}.'.format(release_tag))


def create_plugin_repo() -> str:
    """
    Creates the plugin repo as an XML file
    """
    xml_template = pkg_resources.resource_filename('qgispluginci', 'plugins.xml.template')
    _, xml_repo = mkstemp(suffix='.xml')
    configure_file(xml_template, xml_repo, {})
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

