# Handle submodules SSH

If you have any submodule configured using ssh and not https, you need to change the connection url. For example, on Travis:

````yaml
git:
  submodules: false

before_install:
  # cannot use SSH to fetch submodule
  - sed -i 's#git@github.com:#https://github.com/#' .gitmodules
  - git submodule update --init --recursive
````

When packaging the plugin, it's possible to not update the submodule using CLI options.
