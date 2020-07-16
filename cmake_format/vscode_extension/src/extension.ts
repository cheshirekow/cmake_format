'use strict';

import * as vscode from 'vscode';

function isEmpty(obj: any) {
  for (var key in obj) {
    if (obj.hasOwnProperty(key))
      return false;
  }
  return true;
}

function getWorkspaceFolder(): string | undefined {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage(
      "Unable to get the location of cmake-format executable"
      + " - no active workspace selected");
    return undefined;
  }

  if (!vscode.workspace.workspaceFolders) {
    vscode.window.showErrorMessage(
      "Unable to get the location of clang-format executable"
      + " - no workspaces available");
    return undefined
  }

  const currentDocumentUri = editor.document.uri
  let workspacePath = vscode.workspace.getWorkspaceFolder(currentDocumentUri);
  if (!workspacePath) {
    const fallbackWorkspace = vscode.workspace.workspaceFolders[0];
    vscode.window.showWarningMessage(
      "Unable to deduce the location of clang-format executable for file"
      + "outside the workspace - expanding \${workspaceFolder} to "
      + `'${fallbackWorkspace.name}' path`);
    workspacePath = fallbackWorkspace;
  }
  return workspacePath.uri.path;
}

function varSub(value: string): string {
  if (vscode.workspace.rootPath !== undefined) {
    value = value.replace(/\${workspaceRoot}/g, vscode.workspace.rootPath)
  }
  var workspaceFolder = getWorkspaceFolder();
  if (workspaceFolder !== undefined) {
    value = value.replace(/\${workspaceFolder}/g, workspaceFolder);
  }

  return value
    .replace(/\${cwd}/g, process.cwd())
    .replace(/\${env\.([^}]+)}/g, (sub: string, envName: string) => {
      var value = process.env[envName];
      if (value === undefined) {
        return "";
      } else {
        return value;
      }
    });
}

export function activate(context: vscode.ExtensionContext) {
  console.log('"cmake-format" extension is now active!');

  let disposable = vscode.languages.registerDocumentFormattingEditProvider(
    { scheme: 'file', language: 'cmake' }, {
    provideDocumentFormattingEdits(document: vscode.TextDocument): vscode.TextEdit[] {
      var fs = require('fs')
      var path = require('path')
      var config = vscode.workspace.getConfiguration('cmakeFormat');
      var exePath = config.get("exePath");

      var args = config.get<string[]>("args", [])
      // NOTE(josh): in case the final user-supplied argument is a
      // nargs="*", we need to tell argparse that the next argument
      // ("-") is a positional argument. We do that by adding "--"
      // after the last user-supplied argument and before the "-"
      if (args[args.length - 1] != "--") {
        args = args.concat(["--"]);
      }
      args = args.concat(["-"]);

      var args2: string[] = []
      for (var idx = 0; idx < args.length; idx++) {
        args2.push(varSub(args[idx]));
      }
      args = args2;

      var opts: any = {
        input: document.getText(),
        encoding: 'utf-8'
      };

      var cwd = config.get<string>("cwd");
      if (cwd != null) {
        cwd = varSub(cwd);
      }
      if (cwd == null && document.uri.fsPath != null) {
        cwd = path.dirname(document.uri.fsPath)
        console.log("No cwd configured, using: " + cwd);
      }
      if (cwd == null) {
        var folder = vscode.workspace.getWorkspaceFolder(document.uri);
        if (folder != null) {
          cwd = folder.uri.fsPath;
          console.log("No cwd configured, using workspace path: " + cwd);
        }
      }

      if (cwd != null && fs.statSync(cwd).isDirectory()) {
        opts["cwd"] = cwd;
      } else {
        console.log("Can't use cwd: " + cwd);
      }


      var env: any = {}
      if (config.get("mergeEnv", true)) {
        env = JSON.parse(JSON.stringify(process.env));
      }
      var cenv: any = config.get("env", {});
      if (cenv !== null) {
        var delim = path.delimiter;
        for (var [key, value] of Object.entries(cenv)) {
          if (key.endsWith("PATH")) {
            var items = cenv[key].split(delim);
            if (key in env) {
              items = items.concat(env[key].split(delim));
            }
            env[key] = items.join(delim);
          } else {
            env[key] = value;
          }
        }
      }
      if (!isEmpty(env)) {
        opts["env"] = env;
      }

      const cp = require('child_process')

      // NOTE(josh): execFileSync will throw an Error if the
      // subprocess exits with non-zero status. The vscode GUI will
      // display the stacktrace in the corner.
      var replacementText = cp.execFileSync(exePath, args, opts);
      var firstLine = document.lineAt(0);
      var lastLine = document.lineAt(document.lineCount - 1);
      var wholeRange = new vscode.Range(0,
        firstLine.range.start.character,
        document.lineCount - 1,
        lastLine.range.end.character);
      return [vscode.TextEdit.replace(wholeRange, replacementText)];
    }
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {
}


