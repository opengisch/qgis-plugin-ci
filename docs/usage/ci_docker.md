# Docker

3Liz is maintaining a small docker image of this package : <https://github.com/3liz/docker-qgis-plugin-ci>

This is an example with GitLab-CI running with the Docker image from Docker Hub :

```yaml
  script:
    - >
      docker run
      --rm -w /plugin
      -v ${CI_PROJECT_DIR}:/plugin
      -u $(id -u):$(id -g)
      3liz/qgis-plugin-ci:1.8.3
      package ${CI_COMMIT_REF_NAME}
      --allow-uncommitted-changes
      --plugin-repo-url https://custom.server.url/
```
