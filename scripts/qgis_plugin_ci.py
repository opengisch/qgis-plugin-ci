#!/usr/bin/env python3

import argparse
import configparser
import os
import yaml

from qgispluginci.changelog import ChangelogParser
from qgispluginci.exceptions import ConfigurationNotFound
from qgispluginci.release import release
from qgispluginci.translation import Translation
from qgispluginci.parameters import Parameters


def main():
    # create the top-level parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", help="print the version and exit", action='store_true')

    subparsers = parser.add_subparsers(title='commands', description='qgis-plugin-ci command', dest='command')

    # package
    package_parser = subparsers.add_parser('package', help='creates an archive of the plugin')
    package_parser.add_argument('release_version', help='The version to be released')
    package_parser.add_argument(
        '--transifex-token', help='The Transifex API token. If specified translations will be pulled and compiled.'
    )
    package_parser.add_argument(
        '--plugin-repo-url', help='If specified, a XML repository file will be created in the current directory, the zip URL will use this parameter.'
    )
    package_parser.add_argument(
        '--allow-uncommitted-changes', action='store_true',
        help='If omitted, uncommitted changes are not allowed before packaging. If specified and some changes are '
             'detected, a hard reset on a stash create will be used to revert changes made by qgis-plugin-ci.'
    )
    package_parser.add_argument(
        '--disable-submodule-update', action='store_true',
        help='If omitted, a git submodule is updated. If specified, git submodules will not be updated/initialized before packaging.'
    )

    # changelog
    changelog_parser = subparsers.add_parser('changelog', help='gets the changelog content')
    changelog_parser.add_argument('release_version', help='The version to be released')

    # release
    release_parser = subparsers.add_parser('release', help='release the plugin')
    release_parser.add_argument('release_version', help='The version to be released')
    release_parser.add_argument(
        '--transifex-token',
        help='The Transifex API token. If specified translations will be pulled and compiled.'
    )
    release_parser.add_argument(
        '--github-token',
        help='The Github API token. If specified, the archive will be pushed to an already existing release.'
    )
    release_parser.add_argument(
        '--create-plugin-repo', action='store_true',
        help='Will create a XML repo as a Github release asset. Github token is required.'
    )
    release_parser.add_argument(
        '--allow-uncommitted-changes', action='store_true',
        help='If omitted, uncommitted changes are not allowed before releasing. If specified and some changes are '
             'detected, a hard reset on a stash create will be used to revert changes made by qgis-plugin-ci.'
    )
    release_parser.add_argument(
        '--disable-submodule-update', action='store_true',
        help='If omitted, a git submodule is updated. If specified, git submodules will not be updated/initialized before packaging.'
    )
    release_parser.add_argument('--osgeo-username', help='The Osgeo user name to publish the plugin.')
    release_parser.add_argument('--osgeo-password', help='The Osgeo password to publish the plugin.')

    # pull-translation
    pull_tr_parser = subparsers.add_parser('pull-translation', help='pull translations from Transifex')
    pull_tr_parser.add_argument('transifex_token', help='The Transifex API token')
    pull_tr_parser.add_argument(
        '--compile', action='store_true',
        help='Will compile TS files into QM files'
    )

    # push-translation
    push_tr_parser = subparsers.add_parser('push-translation', help='update strings and push translations')
    push_tr_parser.add_argument('transifex_token', help='The Transifex API token')

    args = parser.parse_args()

    # print the version and exit
    if args.version:
        import pkg_resources
        print('qgis-plugin-ci version: {}'.format(pkg_resources.get_distribution('qgis-plugin-ci').version))
        parser.exit()

    # if no command is passed, print the help and exit
    if not args.command:
        parser.print_help()
        parser.exit()

    exit_val = 0

    if os.path.isfile(".qgis-plugin-ci"):
        arg_dict = yaml.safe_load(open(".qgis-plugin-ci"))
    else:
        config = configparser.ConfigParser()
        config.read("setup.cfg")
        if "qgis-plugin-ci" not in config.sections():
            raise ConfigurationNotFound(
                ".qgis-plugin-ci or setup.cfg with a 'qgis-plugin-ci' section have not been found.")
        arg_dict = dict(config.items("qgis-plugin-ci"))

    parameters = Parameters(arg_dict)

    # PACKAGE
    if args.command == 'package':
        release(
            parameters,
            release_version=args.release_version,
            transifex_token=args.transifex_token,
            allow_uncommitted_changes=args.allow_uncommitted_changes,
            plugin_repo_url=args.plugin_repo_url,
            disable_submodule_update=args.disable_submodule_update,
        )

    # RELEASE
    elif args.command == 'release':
        release(
            parameters,
            release_version=args.release_version,
            transifex_token=args.transifex_token,
            github_token=args.github_token,
            upload_plugin_repo_github=args.create_plugin_repo,
            osgeo_username=args.osgeo_username,
            osgeo_password=args.osgeo_password,
            allow_uncommitted_changes=args.allow_uncommitted_changes,
            disable_submodule_update=args.disable_submodule_update,
        )

    # CHANGELOG
    elif args.command == 'changelog':
        try:
            c = ChangelogParser(parameters.changelog_regexp)
            content = c.content(args.release_version)
            if content:
                print(content)
        except Exception:
            # Better to be safe
            pass

    # TRANSLATION PULL
    elif args.command == 'pull-translation':
        t = Translation(parameters, args.transifex_token)
        t.pull()
        if args.compile:
            t.compile_strings()

    # TRANSLATION PUSH
    elif args.command == 'push-translation':
        t = Translation(parameters, args.transifex_token)
        t.update_strings()
        t.push()

    return exit_val


if __name__ == "__main__":
    exit(main())
