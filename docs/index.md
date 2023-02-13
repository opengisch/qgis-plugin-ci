# {{ title }} - Documentation

> **Description:** {{ description }}  
> **Author and contributors:** {{ author }}  
> **Version:** {{ version }}  
> **Source code:** {{ repo_url }}  
> **Last documentation build:** {{ date_update }}

[![PyPi version badge](https://badgen.net/pypi/v/qgis-plugin-ci)](https://pypi.org/project/qgis-plugin-ci/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/qgis-plugin-ci)](https://pypi.org/project/qgis-plugin-ci/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qgis-plugin-ci)](https://pypi.org/project/qgis-plugin-ci/)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/opengisch/qgis-plugin-ci/master.svg)](https://results.pre-commit.ci/latest/github/opengisch/qgis-plugin-ci/master)

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
misc/credits
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
development/testing
development/history
```

----

## Plugins published using qgis-plugin-ci

<!-- markdownlint-disable MD034 -->

:::::{grid} 2

:::{card}
:link: https://github.com/opengisch/qgis_server_render_geojson/

Render GeoJSON (server)
^^^^^^^^^^^^^^^^^^^^^^^

* deployment on GitHub Releases and plugin repository
* works on GitHub workflows
* barebone implementation, no bells and whistles
:::

:::{card}
:link: https://github.com/3liz/lizmap-plugin/

Lizmap
^^^^^^

* using a `setup.cfg` file
* metadata populated automatically from CHANGELOG.md file
* GitHub release created automatically from Travis
* released on official repository
* translations are committed from Travis to the repository after the release process
* GitLab-CI with Docker is used as well
:::

:::{card}
:link: https://github.com/opengisch/qgis_geomapfish_locator/

GeoMapFish Locator
^^^^^^^^^^^^^^^^^^

* translated on Transifex
* released on official repo
:::

:::{card}
:link: https://github.com/VeriVD/qgis_VeriVD/

VeriVD
^^^^^^

* translated on Transifex
* released on official repo
:::

:::{card}
:link: https://github.com/VeriVD/qgis_VeriVD/

VeriVD
^^^^^^

* released on custom repo as GitHub release
:::

:::{card}
:link: https://github.com/3liz/qgis-pgmetadata-plugin/

pgMetadata
^^^^^^

* Released using GitHub Actions and Transifex

:::

:::{card}
:link: https://github.com/geotribu/qtribu/

QTribu
^^^^^^

* GitHub Actions
* using a `setup.cfg` file
* Used to on custom plugins repository as GitHub release

:::

:::{card}
:link: https://gitlab.com/Oslandia/qgis/landsurveycodesimport/

Land Survey Codes Import
^^^^^^^^^^^^^^^^^^^^^^^^

* Release using **GitLab CI**
* Local translations
* using a `setup.cfg` file

:::

:::{card}
:link: https://gitlab.com/Oslandia/qgis/french_locator_filter/

French Locator Filter
^^^^^^^^^^^^^^^^^^^^^

* Release using **GitLab CI**
* Local translations (no transifex)
* Configured using a `setup.cfg` file
* Both deployed on custom repository on GitLab Pages (on master) on official repository (on git tag)

:::

:::{card}
:link: https://gitlab.com/Oslandia/qgis/thyrsis/

Thyrsis
^^^^^^^

* Packaged and release using **GitLab CI**
* Embed some built external dependencies
* Local translations (no transifex)
* Configured using a `setup.cfg` file
* Both deployed on custom repository on GitLab Pages (on master) on official repository (on git tag)

:::

:::::

<!-- markdownlint-enable MD034 -->
