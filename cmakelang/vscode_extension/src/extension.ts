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

  let rangeDisposable = vscode.languages.registerDocumentRangeFormattingEditProvider(
    { scheme: 'file', language: 'cmake' }, {
    provideDocumentRangeFormattingEdits(document: vscode.TextDocument, range: vscode.Range): vscode.TextEdit[] {
      var fs = require('fs')
      var path = require('path')
      var config = vscode.workspace.getConfiguration('cmakeFormat');
      var exePath = config.get("exePath");
      var args = config.get<string[]>("args", []).concat(["-"]);

      // Expand the selection to whole lines so cmake-format receives
      // complete statements rather than a partial line.
      var startLine = document.lineAt(range.start.line);
      var endLine = document.lineAt(range.end.line);
      var fullRange = new vscode.Range(
        range.start.line, startLine.range.start.character,
        range.end.line, endLine.range.end.character);

      // cmake-format always emits output starting at column 0; it has no
      // notion of where the selection sits in the surrounding block. To keep
      // the selection aligned with its context we detect the leading
      // indentation of the selection, strip it from every line before feeding
      // the text to cmake-format, then re-apply it to the formatted result.
      var selectedText = document.getText(fullRange);
      var selectedLines = selectedText.split(/\r?\n/);

      // Determine the base indentation from the first non-blank line. Using
      // the smallest indent across all lines would be more robust, but the
      // first line of a well-formed selection is the statement head and is the
      // anchor the rest of the block aligns to.
      var baseIndent = "";
      for (var li = 0; li < selectedLines.length; li++) {
        var m = selectedLines[li].match(/^[ \t]*/);
        if (selectedLines[li].trim().length > 0) {
          baseIndent = m ? m[0] : "";
          break;
        }
      }

      // Strip the base indentation from each line so cmake-format sees a
      // top-level (column 0) statement and lays out internal alignment
      // correctly. Lines that don't start with the full base indent are left
      // as-is to avoid corrupting unexpected content.
      var dedentedLines = selectedLines.map(function (line: string) {
        if (baseIndent.length > 0 && line.startsWith(baseIndent)) {
          return line.substring(baseIndent.length);
        }
        // Fall back to trimming whatever leading whitespace exists, but only
        // up to the base indent width, to handle mixed indentation gracefully.
        return line.replace(/^[ \t]*/, function (ws: string) {
          return ws.length <= baseIndent.length ? "" : ws.substring(baseIndent.length);
        });
      });

      var opts: any = {
        input: dedentedLines.join("\n"),
        encoding: 'utf-8'
      };

      var cwd = config.get("cwd");
      if (cwd == null) {
        var folder = vscode.workspace.getWorkspaceFolder(document.uri);
        if (folder != null) {
          cwd = folder.uri.fsPath;
          console.log("No cwd configured, using workspace path: " + cwd);
        }
      }
      if (cwd == null && document.uri.fsPath != null) {
        cwd = path.dirname(document.uri.fsPath)
        console.log("No cwd configured, no workspace path, using: " + cwd);
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
      var replacementText = cp.execFileSync(exePath, args, opts);
      // cmake-format appends a trailing newline; drop it so we don't
      // introduce an extra blank line into the middle of the file.
      replacementText = replacementText.replace(/\r?\n$/, "");

      // Re-apply the base indentation that we stripped before formatting so
      // the block lines back up with its surrounding context. Blank lines are
      // left empty rather than padded with trailing whitespace.
      if (baseIndent.length > 0) {
        replacementText = replacementText
          .split("\n")
          .map(function (line: string) {
            return line.length > 0 ? baseIndent + line : line;
          })
          .join("\n");
      }
      return [vscode.TextEdit.replace(fullRange, replacementText)];
    }
  });

  context.subscriptions.push(disposable);
  context.subscriptions.push(rangeDisposable);
}

export function deactivate() {
}


