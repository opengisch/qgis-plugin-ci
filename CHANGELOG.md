# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!-- ## Unreleased [{version_tag}](https://github.com/opengisch/qgis-plugin-ci/releases/tag/{version_tag}) - YYYY-MM-DD -->

## Unreleased

## 2.5.3 - 2023-02-10

<!-- Release notes generated using configuration in .github/release.yml at 2.5.3 -->

### Bugs fixes 🐛

* Bump git hooks to fix pre-commit fail because of isort by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/187>

### Features and enhancements 🎉

* Add missing aliases to release subcommand by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/164>
* Python - Use Python fstrings everywhere by @Gustry in <https://github.com/opengisch/qgis-plugin-ci/pull/166>
* Add option to use a custom plugin server by @towa in <https://github.com/opengisch/qgis-plugin-ci/pull/181>

### Documentation 📖

* Complete latest releases notes to changelog by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/163>

### Other Changes

* Avoid duplicated dependencies listing by loading dependencies from requirements files by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/188>

### New Contributors

* @towa made their first contribution in <https://github.com/opengisch/qgis-plugin-ci/pull/181>

## 2.5.2 - 2022-09-26

* Align xmlrpc verbosity on CLI option by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/161>

## 2.5.1 - 2022-09-22

* Fix 159: Add missing parameters and set a default value by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/160>

## 2.5.0 - 2022-09-22

* fix Experimental flag is not correct for a pre-release tag in the XML by @3nids in <https://github.com/opengisch/qgis-plugin-ci/pull/150>
* Fix regression in 2.4 where zip was not compressed by @ivanlonel in <https://github.com/opengisch/qgis-plugin-ci/pull/151>
* Use built-in version argument by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/153>
* use concurrency to avoid multiple workflow running at once by @3nids in <https://github.com/opengisch/qgis-plugin-ci/pull/154>
* Do not run pyqt5ac if there is no qrc file by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/157>
* Feature: add verbosity option and improve log by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/156>
* Handle missing changelog when latest is passed by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/158>
* Improve release workflow enabling auto changelog by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/149>
* Update and clean git hooks by @Guts in <https://github.com/opengisch/qgis-plugin-ci/pull/152>

## 2.4.0 - 2022-08-25

* Keep files permissions when creating zip file by @jmkerloch #129
* Update dependencies
* Documentation improvements

## 2.3.0 - 2022-03-17

* Add some metadata in the `metadata.txt` when packaging such as commit number, commit SHA1 and date if these keys are presents

## 2.2.0 - 2022-03-17

* Allow to release a version (1.2.3) which is different from the release tag (v1.2.3) (#120)

## 2.1.2 - 2022-02-15

* Raise an error if a built resource is present in source and the names conflicts by @3nids

## 2.1.1 - 2022-01-20

* Fix a regression from 2.1.0 when the changelog command is used without a configuration file

## 2.1.0 - 2022-01-10

* Add the possibility to choose the changelog filepath in the configuration file with `changelog_path`
* Add some aliases in the command line for some parameters
* Update the documentation

## 2.0.1 - 2021-05-11

* Fix an issue when packaging this project on <https://pypi.org/>

## 2.0.0 - 2021-05-06

* Add a dedicated website for the documentation <https://opengisch.github.io/qgis-plugin-ci/>
* Improve the changelog parser :
  * The `changelog_regexp` parameter has been removed
  * The CHANGELOG.md must follow [semantic versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/)
  * The `experimental` flag is determined automatically if the package name is following the semantic versioning
* Add a special keyword `latest` to package the latest version described in a CHANGELOG.md file
* Possible to install the repository using pip install with the GIT URL

## 1.8.4 - 2020-09-07

* Separate python files and UI files in the temporary PRO file (#29)

## 1.8.3 - 2020-08-25

* Keep the plugin path when creating the ZIP
* Rename qgis_plugin_ci_testing to qgis_plugin_CI_testing to have a capital letter
* Update readme about plugin_path

## 1.8.2 - 2020-08-05

* Run travis on tags too (#24)

## 1.8.1 - 2020-08-05

* better support of spaces in plugin name
* Use underscore instead of hyphen for plugin name #22 (#23)

## 1.8.0 - 2020-07-16

* Create temporary .pro file to make pylupdate5 work with unicode char (#19)

## 0.1.2 - 2017-07-23

(This version note is used in unit-tests)

* Tag without "v" prefix
* Add a CHANGELOG.md file for testing
