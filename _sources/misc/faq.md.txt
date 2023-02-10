# Frequently Asked Questions

## Unknown error

If you get this message:

```log
A fault occurred
Fault code: 1
Fault string: Unknown error, ['  File "/usr/local/lib/python3.7/site-packages/rpc4django/xmlrpcdispatcher.py", line 84, in dispatch\n    response = self._dispatch(method, params, **kwargs)\n', '  File "/usr/local/lib/python3.7/site-packages/rpc4django/xmlrpcdispatcher.py", line 121, in _dispatch\n    return func(*params, **kwargs)\n', '  File "./plugins/api.py", line 121, in plugin_upload\n    raise Fault(1, e.message)\n']
```

Try to upload manually the plugin through the web UI on <https://plugins.qgis.org> and follow the error message.

It occurs for many reasons:

- the plugin name is not matching the previous plugin versions

## How can I merge many XML files into one ?

QGIS-Plugin-CI can generate the `plugins.xml` file, per plugin.
If you want to merge many XML files into one to have a single QGIS plugin repository providing many plugins,
you should check [QGIS-Plugin-Repo](https://github.com/3liz/qgis-plugin-repo).
It's designed to run on CI after QGIS-Plugin-CI.
