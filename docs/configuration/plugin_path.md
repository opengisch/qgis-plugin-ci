# Plugin source path

The plugin path should be named in a distinctive form for the plugin
as it will be used in QGIS for the plugin folder name.
For instance, `my_super_transformer` for _My Super Transformer_ plugin.

Also, [`use_project_slug_as_plugin_directory`](/_apidoc/qgispluginci.parameters) can be used to alter this behavior.
If the source directory is not at the top level, the [`project_slug`](/_apidoc/qgispluginci.parameters)
will automatically be used in any case.

Side note, the plugin path shouldn't contain any dash character.
