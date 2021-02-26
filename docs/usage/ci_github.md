# GitHub workflows

qgis-plugin-ci integrates nicely with github workflows. The following example automatically uploads plugins to releases and to the plugin repository when a new release is created on github.

All you need to do is adding `OSGEO_PASSWORD` to the secrets in the repository settings. Note that the `GITHUB_TOKEN` is available automatically without any configuration.

Save this file as `.github/workflows/release.yaml`:

```yaml
on:
  release:
    types: published

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python 3.8
        uses: actions/setup-python@v1
        with:
          python-version: 3.8

       # Needed if the plugin is using Transifex, to have the lrelease command
       # - name: Install Qt lrelease
       #   run: |
       #    sudo apt-get update
       #    sudo apt-get install qt5-default qttools5-dev-tools

      - name: Install qgis-plugin-ci
        run: pip3 install qgis-plugin-ci

      - name: Deploy plugin
        run: >-
          qgis-plugin-ci
          release ${GITHUB_REF/refs\/tags\//}
          --github-token ${{ secrets.GITHUB_TOKEN }}
          --osgeo-username ${{ secrets.OSGEO_USER }}
          --osgeo-password ${{ secrets.OSGEO_PASSWORD }}
```
