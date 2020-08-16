# Change Log

Note that the vscode extension release version matches the
cmake-format release version on [pypi][2].

### 0.6.11

- Add variable substitution for ${workspaceFolder} and ${workspaceRoot} to
  configuration entries

### 0.6.10

- Fix typos in environment handling

### 0.6.6

`--` is automatically appended to the argument vector used to call
`cmake-format` (if it does not already end with `--`) so that any user-config
command line options are propertly terminated before the automatic positional
arguments are appended.

### 0.6.0

No functional changes, just documentation update.

### 0.5.5

- Modify vscode extension cwd  to better support subtree configuration files
- Fix vscode extension args type configuration

### 0.4.2

Fixed bug with using workspace path as `cwd` when calling `cmake-foramt`.

## 0.4.1
- Initial release
- Working callout to cmake-format with configuration options.

[2]: https://pypi.org/project/cmakelang/

