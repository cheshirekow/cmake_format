# Notes

## Setup

* Add nodesource PPA:
```
deb https://deb.nodesource.com/node_8.x xenial main
deb-src https://deb.nodesource.com/node_8.x xenial main
```

* `sudo apt-get install nodejs node-typescript`
* Create user-global node tree:
  1. `mkdir "${HOME}/.npm-packages"`
  2. `nano ~/.npmrc` to contain `prefix=${HOME}/.npm-packages`
  3. Add the following to `~/.bashrc`:
```
NPM_PACKAGES="${HOME}/.npm-packages"
PATH="$NPM_PACKAGES/bin:$PATH"
# Unset manpath so we can inherit from /etc/manpath via the `manpath` command
unset MANPATH # delete if you already modified MANPATH elsewhere in your config
export MANPATH="$NPM_PACKAGES/share/man:$(manpath)"
```

## Build and test the extension

* Run `npm install -g vscode vsce` (after global config for user)
* Run `npm install` in the source tree to get all the dependencies.
* Open this directory in vscode, then press f5 to launch debugger

## Create and publish a package

* See https://code.visualstudio.com/docs/extensions/publish-extension
* Build and publish with:

```
vsce package --baseImagesUrl https://raw.githubusercontent.com/cheshirekow/cmake_format/master/cmake_format/vscode_extension
vsce publish --baseImagesUrl https://raw.githubusercontent.com/cheshirekow/cmake_format/master/cmake_format/vscode_extension
```

* See https://code.visualstudio.com/docs/extensions/testing-extensions for CI notes
