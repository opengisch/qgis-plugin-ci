# Release

This command is specific for plugins hosted on GitHub.

```bash
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
  -c --allow-uncommitted-changes
                        If omitted, uncommitted changes are not allowed before
                        releasing. If specified and some changes are detected,
                        a hard reset on a stash create will be used to revert
                        changes made by qgis-plugin-ci.
  -d --disable-submodule-update
                        If omitted, a git submodule is updated. If specified, git submodules will not be updated/initialized before packaging.
  --osgeo-username OSGEO_USERNAME
                        The Osgeo user name to publish the plugin.
  --osgeo-password OSGEO_PASSWORD
                        The Osgeo password to publish the plugin.
```
