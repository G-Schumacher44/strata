import * as vscode from 'vscode';
import {
  detectStrata,
  promptInstall,
  buildGraph,
  impactFromScope,
  navigateField,
  resolveRepoPath,
} from './clibridge';
import { StrataGovernanceDiagnostics } from './govdiagnostics';

const LOOKML_GLOBS = ['**/*.lkml', '**/*.view.lkml', '**/*.model.lkml', '**/*.explore.lkml'];
const OUTPUT_CHANNEL_NAME = 'Strata';

let outputChannel: vscode.OutputChannel | undefined;

function getOutput(): vscode.OutputChannel {
  if (!outputChannel) {
    outputChannel = vscode.window.createOutputChannel(OUTPUT_CHANNEL_NAME);
  }
  return outputChannel;
}

function showJSON(label: string, data: unknown): void {
  const out = getOutput();
  out.clear();
  out.appendLine(`=== ${label} ===`);
  out.appendLine(JSON.stringify(data, null, 2));
  out.show(true);
}

function showError(message: string): void {
  const out = getOutput();
  out.clear();
  out.appendLine(`ERROR: ${message}`);
  out.show(true);
  void vscode.window.showErrorMessage(`Strata: ${message}`);
}

function isLookMLFile(uri: vscode.Uri): boolean {
  const name = uri.fsPath.toLowerCase();
  return name.endsWith('.lkml');
}

function getWordUnderCursor(editor: vscode.TextEditor): string | undefined {
  const position = editor.selection.active;
  const wordRange = editor.document.getWordRangeAtPosition(position, /[\w.]+/);
  if (!wordRange) {
    return undefined;
  }
  return editor.document.getText(wordRange);
}

function renderNavigateWebview(
  context: vscode.ExtensionContext,
  anchor: string,
  data: Record<string, unknown>
): void {
  const panel = vscode.window.createWebviewPanel(
    'strataNavigate',
    `Strata: ${anchor}`,
    vscode.ViewColumn.Beside,
    { enableScripts: false }
  );

  const json = JSON.stringify(data, null, 2);
  const anchorType = String(data['anchor_type'] ?? 'unknown');

  panel.webview.html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Strata Navigate: ${anchor}</title>
  <style>
    body { font-family: var(--vscode-font-family); font-size: 13px; padding: 16px; color: var(--vscode-foreground); background: var(--vscode-editor-background); }
    h1 { font-size: 1.1em; margin-bottom: 4px; }
    .badge { display: inline-block; background: var(--vscode-badge-background); color: var(--vscode-badge-foreground); border-radius: 3px; padding: 1px 6px; font-size: 0.85em; margin-left: 8px; }
    pre { background: var(--vscode-textBlockQuote-background); border: 1px solid var(--vscode-panel-border); border-radius: 4px; padding: 12px; overflow-x: auto; white-space: pre-wrap; word-break: break-all; font-size: 12px; }
  </style>
</head>
<body>
  <h1>Navigate: <code>${anchor}</code> <span class="badge">${anchorType}</span></h1>
  <pre>${json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
</body>
</html>`;
}

export function activate(context: vscode.ExtensionContext): void {
  const govDiag = new StrataGovernanceDiagnostics();
  context.subscriptions.push(govDiag);

  if (!detectStrata()) {
    promptInstall();
  }

  const cmdBuildGraph = vscode.commands.registerCommand('strata.buildGraph', () => {
    if (!detectStrata()) {
      promptInstall();
      return;
    }

    const repoPath = resolveRepoPath();
    if (!repoPath) {
      showError('No workspace folder open and strata.repoPath not configured.');
      return;
    }

    void vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: 'Strata: Building graph…',
        cancellable: false,
      },
      () => {
        return new Promise<void>((resolve) => {
          const result = buildGraph(repoPath);
          if (result.ok) {
            showJSON('Build Graph Result', result.data);
          } else {
            showError(result.error ?? 'Unknown error building graph');
          }
          resolve();
        });
      }
    );
  });

  const cmdImpact = vscode.commands.registerCommand('strata.impactAnalysis', () => {
    if (!detectStrata()) {
      promptInstall();
      return;
    }

    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      void vscode.window.showWarningMessage('Strata: Open a LookML file first.');
      return;
    }

    if (!isLookMLFile(editor.document.uri)) {
      void vscode.window.showWarningMessage('Strata: Impact Analysis requires a .lkml file.');
      return;
    }

    const filePath = editor.document.uri.fsPath;
    const repoPath = resolveRepoPath();

    void vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: 'Strata: Analysing impact…',
        cancellable: false,
      },
      () => {
        return new Promise<void>((resolve) => {
          const result = impactFromScope(filePath, repoPath);
          if (result.ok) {
            showJSON(`Impact Analysis: ${editor.document.fileName.split('/').pop()}`, result.data);
          } else {
            showError(result.error ?? 'Unknown error during impact analysis');
          }
          resolve();
        });
      }
    );
  });

  const cmdNavigate = vscode.commands.registerCommand('strata.navigateField', () => {
    if (!detectStrata()) {
      promptInstall();
      return;
    }

    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      void vscode.window.showWarningMessage('Strata: Open a LookML file and place cursor on a field/view name.');
      return;
    }

    const anchor = getWordUnderCursor(editor);
    if (!anchor) {
      void vscode.window.showWarningMessage('Strata: No word found under cursor.');
      return;
    }

    const repoPath = resolveRepoPath();

    void vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: `Strata: Navigating '${anchor}'…`,
        cancellable: false,
      },
      () => {
        return new Promise<void>((resolve) => {
          const result = navigateField(anchor, repoPath);
          if (result.ok && result.data) {
            renderNavigateWebview(context, anchor, result.data);
          } else {
            showError(result.error ?? 'Unknown error during navigation');
          }
          resolve();
        });
      }
    );
  });

  const cmdRefreshDiag = vscode.commands.registerCommand('strata.refreshDiagnostics', () => {
    if (!detectStrata()) {
      promptInstall();
      return;
    }
    const repoPath = resolveRepoPath();
    govDiag.refresh(repoPath);
    void vscode.window.showInformationMessage('Strata: Governance diagnostics refreshed.');
  });

  const saveListener = vscode.workspace.onDidSaveTextDocument((doc) => {
    if (!isLookMLFile(doc.uri)) {
      return;
    }
    const repoPath = resolveRepoPath();
    govDiag.scheduledRefresh(repoPath);
  });

  const watcher = vscode.workspace.createFileSystemWatcher(`{${LOOKML_GLOBS.join(',')}}`);

  context.subscriptions.push(
    cmdBuildGraph,
    cmdImpact,
    cmdNavigate,
    cmdRefreshDiag,
    saveListener,
    watcher
  );
}

export function deactivate(): void {
  outputChannel?.dispose();
}
