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
- set the `experimental` flag according to the tag if needed

:book: For further information, see [the documentation](https://opengisch.github.io/qgis-plugin-ci/).

QGIS-Plugin-CI is best served if you use these two conventions :

* [Semantic versioning](https://semver.org/)
* [Keep A Changelog](https://keepachangelog.com)

## Command line

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

## Requirements

- The code is under a **git** repository (`git archive` is used to bundle the plugin)
- There is no uncommitted changes when doing a package/release (there is an option to allow this)
- A configuration at the top directory either in `.qgis-plugin-ci` or in `setup.cfg` with a `[qgis-plugin-ci]` section.
- The source files of the plugin are within a sub-directory. The name of this directory will be used for the zip file.

## QRC and UI files

- Any .qrc file in the source top directory (plugin_path) will be compiled and output as filename_rc.py. You can then import it using `import plugin_path.resources_rc`
- Currently, qgis-plugin-ci does not compile any .ui file.

## Publishing plugins

When releasing, you can publish the plugin :

1. In the official QGIS plugin repository. You need to provide user name and password for your Osgeo account.
2. As a custom repository in Github releases and which can be added later in QGIS. The address will be: https://github.com/__ORG__/__REPO__/releases/latest/download/plugins.xml

Both can be achieved in the same process.

## Pre-release and experimental

In the case of a pre-release (either from the tag name according to [Semantic Versioning](https://semver.org/) or from the GitHub release), the plugin will be flagged as experimental.
If pushed to the QGIS plugin repository, the QGIS minimum version will be raised to QGIS 3.14 (only 3.14 and above support testing of experimental versions).

The tool will recognise any label use as a suffix to flag it as pre-release :

* `10.1.0-beta1`
* `3.4.0-rc.2`

## Debug

In any Python module, you can have a global variable as `DEBUG = True`, which will be changed to `False` when packaging the plugin.
