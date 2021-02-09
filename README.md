# QGIS Plugin CI

Contains scripts to perform automated testing and deployment for QGIS plugins.
These scripts are written for and tested on GitHub, Travis-CI, github workflows and Transifex.

 - Deploy plugin releases on QGIS official plugin repository
 - Publish plugin in Github releases, option to deploy a custom repository
 - Easily integrated in Travis-CI or github workflows
 - Completely handle translations with Transifex:
    - create the project and the languages
    - pull and push translations
    - all TS/QM files can be managed on the CI, the `i18n` folder can be omitted from the Git repository
 - `changelog` section in the metadata.txt can be populated if the CHANGELOG.md is present
   
# Command line

```commandline
usage: qgis-plugin-ci [-h] [-v]
                      {package,changelog,release,pull-translation,push-translation}
                      ...

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         print the version and exit

commands:
  qgis-plugin-ci command

  {package,changelog,release,pull-translation,push-translation}
    package             creates an archive of the plugin
    changelog           gets the changelog content
    release             release the plugin
    pull-translation    pull translations from Transifex
    push-translation    update strings and push translations
```

## Package

This command is not specific to the hosting platform (GitLab, GitHub…)

```commandline
usage: qgis-plugin-ci package [-h]
                              [--transifex-token TRANSIFEX_TOKEN]
                              [--plugin-repo-url PLUGIN_REPO_URL]
                              [--allow-uncommitted-changes]
                              release_version

positional arguments:
  release_version       The version to be released

optional arguments:
  -h, --help            show this help message and exit
  --transifex-token TRANSIFEX_TOKEN
                        The Transifex API token. If specified translations
                        will be pulled and compiled.
  --plugin-repo-url PLUGIN_REPO_URL
                        If specified, a XML repository file will be created in the current directory, the zip URL will use this parameter.
  --allow-uncommitted-changes
                        If omitted, uncommitted changes are not allowed before
                        packaging. If specified and some changes are detected,
                        a hard reset on a stash create will be used to revert
                        changes made by qgis-plugin-ci.
  --disable-submodule-update
                        If omitted, a git submodule is updated. If specified, git submodules will not be updated/initialized before packaging.

```

## Release

This command is specific for plugins hosted on GitHub.

```commandline
usage: qgis-plugin-ci release [-h] [--transifex-token TRANSIFEX_TOKEN]
                              [--github-token GITHUB_TOKEN]
                              [--create-plugin-repo]
                              [--allow-uncommitted-changes]
                              [--osgeo-username OSGEO_USERNAME]
                              [--osgeo-password OSGEO_PASSWORD]
                              release_version

positional arguments:
  release_version       The version to be released

optional arguments:
  -h, --help            show this help message and exit
  --transifex-token TRANSIFEX_TOKEN
                        The Transifex API token. If specified translations
                        will be pulled and compiled.
  --github-token GITHUB_TOKEN
                        The Github API token. If specified, the archive will
                        be pushed to an already existing release.
  --create-plugin-repo  Will create a XML repo as a Github release asset.
                        Github token is required.
  --allow-uncommitted-changes
                        If omitted, uncommitted changes are not allowed before
                        releasing. If specified and some changes are detected,
                        a hard reset on a stash create will be used to revert
                        changes made by qgis-plugin-ci.
  --disable-submodule-update
                        If omitted, a git submodule is updated. If specified, git submodules will not be updated/initialized before packaging.
  --osgeo-username OSGEO_USERNAME
                        The Osgeo user name to publish the plugin.
  --osgeo-password OSGEO_PASSWORD
                        The Osgeo password to publish the plugin.
```

## Pull translations

```commandline
usage: qgis-plugin-ci pull-translation [-h] [--compile] transifex_token

positional arguments:
  transifex_token  The Transifex API token

optional arguments:
  -h, --help       show this help message and exit
  --compile        Will compile TS files into QM files
```

## Push translations

```commandline
usage: qgis-plugin-ci push-translation [-h] transifex_token

positional arguments:
  transifex_token  The Transifex API token

optional arguments:
  -h, --help       show this help message and exit
```

## Changelog

By default, the changelog command will work with a file formatted like [this changelog.md file](./CHANGELOG.md).
If your format is different, you must use a different `changelog_regexp` expression to parse it in your settings.

```commandline
usage: qgis-plugin-ci changelog [-h] release_version

positional arguments:
  release_version  The version to be released

optional arguments:
  -h, --help       show this help message and exit
```

## Requirements

* The code is under a __git__ repository (`git archive` is used to bundle the plugin)
* There is no uncommitted changes when doing a package/release (there is an option to allow this)
* A configuration at the top directory either in `.qgis-plugin-ci` or in `setup.cfg` with a `[qgis-plugin-ci]` section.
* The source files of the plugin are within a sub-directory. The name of this directory will be used for the zip file.

## The configuration file

The plugin must have a configuration, located at the top directory:
* either you use a `.qgis-plugin-ci` file
* or you use a `[qgis-plugin-ci]` section in a `setup.cfg` file (which is used by many other tool).

In the configuration, you should at least provide the following configuration:

* `plugin_path`, the folder where the source code is located

Side note, the plugin path shouldn't have any dash character.

You can find a template `.qgis-plugin-ci` in this repository.
You can read the docstring of the file `qgispluginci/parameters.py`
to know parameters which are available in the file.

### Examples

* `.qgis-plugin-ci`

```yaml
plugin_path: qgis_plugin_ci_testing
github_organization_slug: opengisch
project_slug: qgis-plugin-ci
```

* `setup.cfg`

```ini
[qgis-plugin-ci]
plugin_path = QuickOSM
github_organization_slug = 3liz
project_slug = QuickOSM
```

## QRC and UI files

- Any .qrc file in the source top directory (plugin_path) will be compiled and output as filename_rc.py. You can then import it using ``import plugin_path.resources_rc``
- Currently, qgis-plugin-ci does not compile any .ui file.

## Publishing plugins

When releasing, you can publish the plugin :

1. In the official QGIS plugin repository. You need to provide user name and password for your Osgeo account.
2. As a custom repository in Github releases and which can be added later in QGIS. The address will be: https://github.com/__ORG__/__REPO__/releases/latest/download/plugins.xml

Both can be achieved in the same process.

## Pre-release and experimental

In the case of a pre-release (from GitHub), the plugin will be flagged as experimental.
If pushed to the QGIS plugin repository, the QGIS minimum version will be raised to QGIS 3.14 (only 3.14 and above support testing of experimental versions).

## Debug

In any Python module, you can have a global variable as `DEBUG = True`, which will be changed to `False` when packaging the plugin.

# Sample plugins

These plugins are using this tool, with different configurations as examples:

* https://github.com/opengisch/qgis_server_render_geojson
  * deployment on github releases and plugin repository
  * works on gihtub workflows
  * barebone implementation, no bells and whistles
* https://github.com/opengisch/qgis_geomapfish_locator:
  * translated on Transifex
  * released on official repo
* https://github.com/VeriVD/qgis_VeriVD
  * released on custom repo as GitHub release
* https://github.com/3liz/lizmap-plugin
  * using a `setup.cfg` file
  * metadata populated automatically from CHANGELOG.md file
  * GitHub release created automatically from Travis
  * released on official repository
  * translations are committed from Travis to the repository after the release process
  * GitLab-CI with Docker is used as well
* https://github.com/3liz/qgis-pgmetadata-plugin
  * Released using GitHub Actions and Transifex
