# {{ title }} - Documentation

> **Author and contributors:** {{ author }}
> **Version:** {{ version }}
> **Source code:** {{ repo_url }}

## Installation

Package is available on [PyPi](https://pypi.org/project/qgis-plugin-ci/):

```bash
pip install qgis-plugin-ci
```

```{toctree}
---
caption: Configuration
maxdepth: 1
---
configuration/options
configuration/exclude
configuration/submodules
configuration/translation
```

```{toctree}
---
caption: Use the CLI
maxdepth: 1
---
usage/cli_changelog
usage/cli_package
usage/cli_release
usage/cli_translation
```

```{toctree}
---
caption: Use in CI/CD platforms
maxdepth: 1
---
usage/ci_github
usage/ci_gitlab
usage/ci_docker
usage/ci_travis
```

```{toctree}
---
caption: Miscellaneous
maxdepth: 1
---
misc/faq
```

```{toctree}
---
caption: Contribution guide
maxdepth: 1
---
Code documentation <_apidoc/modules>
development/contribute
development/environment
development/documentation
development/packaging
development/history
```

## Gallery

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
