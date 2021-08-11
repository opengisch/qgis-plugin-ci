# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!-- ## Unreleased [{version_tag}](https://github.com/opengisch/qgis-plugin-ci/releases/tag/{version_tag}) - YYYY-MM-DD -->

## Unreleased

* Add some aliases in the command line for some parameters
* Update the documentation
* Fix some changelog file not found when used in a sub folder

## 2.0.1 - 2021-05-11

- Fix an issue when packaging this project on https://pypi.org/

## 2.0.0 - 2021-05-06

- Add a dedicated website for the documentation https://opengisch.github.io/qgis-plugin-ci/
- Improve the changelog parser :
  - The `changelog_regexp` parameter has been removed
  - The CHANGELOG.md must follow [semantic versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/)
  - The `experimental` flag is determined automatically if the package name is following the semantic versioning
- Add a special keyword `latest` to package the latest version described in a CHANGELOG.md file
- Possible to install the repository using pip install with the GIT URL

## 1.8.4 - 2020-09-07

- Separate python files and UI files in the temporary PRO file (#29)

## 1.8.3 - 2020-08-25

- Keep the plugin path when creating the ZIP
- Rename qgis_plugin_ci_testing to qgis_plugin_CI_testing to have a capital letter
- Update readme about plugin_path

## 1.8.2 - 2020-08-05

- Run travis on tags too (#24)

## 1.8.1 - 2020-08-05

- better support of spaces in plugin name
- Use underscore instead of hyphen for plugin name #22 (#23)

## 1.8.0 - 2020-07-16

- Create temporary .pro file to make pylupdate5 work with unicode char (#19)

## 0.1.2 - 2017-07-23

(This version note is used in unit-tests)

- Tag without "v" prefix
- Add a CHANGELOG.md file for testing
