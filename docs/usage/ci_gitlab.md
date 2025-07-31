# GitLab CI

qgis-plugin-ci integrates nicely with GitLab CI. The following example automatically uploads plugins to the plugin repository when a new tag is created on GitLab.

All you need to do is adding `OSGEO_USER_NAME` and `OSGEO_USER_PASSWORD` to the CI/CD variables in the repository settings.

Save this file as `.gitlab-ci.yml`:

```yaml
stages:
  - 🚀 deploy

deploy:qgis-repository:
  stage: 🚀 deploy
  image: python:3.11
  rules:
    - if: '$CI_COMMIT_TAG'
  before_script:
    - apt update
    - apt install -y git
# Uncomment if plugin use translations
#     - apt install -y qt5-qmake qttools5-dev-tools
#     - python -m pip install -U pyqt5-tools
    - python -m pip install -U qgis-plugin-ci
  script:
    - echo "Deploying the version ${CI_COMMIT_TAG} plugin to QGIS Plugins Repository with the user ${OSGEO_USER_NAME}"
# Uncomment if plugin use translations
#     # Amend gitignore to include translation files with qgis-plugin-ci
#     - sed -i "s|^*.qm.*| |" .gitignore
#     # git tracks new files
#     - git add $PROJECT_FOLDER/resources/i18n/*.qm
    - qgis-plugin-ci release ${CI_COMMIT_TAG}
        --osgeo-username $OSGEO_USER_NAME
        --osgeo-password $OSGEO_USER_PASSWORD
        --allow-uncommitted-changes
```
