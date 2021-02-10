# Exclude files in the plugin archive

If you want to avoid some files to be shipped with your plugin, create a `.gitattributes` file in which you can specify the files to ignore. For instance:

```gitignore
resources.qrc export-ignore
```
