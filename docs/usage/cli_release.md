# Release

This command is specific for plugins hosted on GitHub.

```bash
usage: qgis-plugin-ci release [-h] [--release-tag RELEASE_TAG]
                              [--transifex-token TRANSIFEX_TOKEN]
                              [--github-token GITHUB_TOKEN] [-r] [-c] [-d]
                              [--alternative-repo-url ALTERNATIVE_REPO_URL]
                              [--qgis-token QGIS_TOKEN]
                              [--osgeo-username OSGEO_USERNAME]
                              [--osgeo-password OSGEO_PASSWORD]
                              release_version

positional arguments:
  release_version       The version to be released (x.y.z).

options:
  -h, --help            show this help message and exit
  --release-tag RELEASE_TAG
                        The release tag, if different from the version (e.g. vx.y.z).
  --transifex-token TRANSIFEX_TOKEN
                        The Transifex API token. If specified translations will be pulled and
                        compiled.
  --github-token GITHUB_TOKEN
                        The GitHub API token. If specified, the archive will be pushed to an
                        already existing release.
  -r, --create-plugin-repo
                        Will create a XML repo as a Github release asset. Github token is
                        required.
  -c, --allow-uncommitted-changes
                        If omitted, uncommitted changes are not allowed before releasing. If
                        specified and some changes are detected, a hard reset on a stash
                        create will be used to revert changes made by qgis-plugin-ci.
  -d, --disable-submodule-update
                        If omitted, a git submodule is updated. If specified, git submodules
                        will not be updated/initialized before packaging.
  --alternative-repo-url ALTERNATIVE_REPO_URL
                        The URL of the endpoint to publish the plugin (defaults to
                        plugins.qgis.org)
  -a ASSET_PATH, --asset-path ASSET_PATH
                        An additional asset path to add. Can be specified multiple times.
  --qgis-token QGIS_TOKEN
                        The token from https://plugins.qgis.org to publish the plugin. Incompatible with the OSGeo user name.
  --osgeo-username OSGEO_USERNAME
                        The OSGeo user name to publish the plugin. Incompatible with QGIS token.
  --osgeo-password OSGEO_PASSWORD
                        The OSGeo password to publish the plugin. Incompatible with QGIS token.
```

If the exit code is `2`, it means the upload to the QGIS plugin server has failed.

## Additional metadata

When packaging the plugin, some extra metadata information can be added if these keys are present in the `metadata.txt`:

* `commitNumber=` : the commit number in the branch otherwise 1 on a tag
* `commitSha1=` : the commit ID
* `dateTime=` : the date time in UTC format when the packaging is done

:::{tip}
These extra parameters are specific to QGIS Plugin CI, so it's strongly recommended storing them below a dedicated section:

```ini
[tool:qgis-plugin-ci]
commitNumber=
commitSha1=
dateTime=
```

:::
