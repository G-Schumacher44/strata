import * as path from 'path';
import * as vscode from 'vscode';
import { detectStrata, queryOrphans, OrphanRecord } from './clibridge';

const DEBOUNCE_MS = 1500;

export class StrataGovernanceDiagnostics {
  private readonly collection: vscode.DiagnosticCollection;
  private debounceHandle: ReturnType<typeof setTimeout> | undefined;

  constructor() {
    this.collection = vscode.languages.createDiagnosticCollection('strata-governance');
  }

  refresh(repoRoot?: string): void {
    if (!detectStrata()) {
      this.collection.clear();
      return;
    }

    const result = queryOrphans(repoRoot);
    if (!result.ok || !result.data) {
      return;
    }

    this.collection.clear();

    const byFile = new Map<string, vscode.Diagnostic[]>();

    for (const orphan of result.data) {
      const diag = this.toDiagnostic(orphan);
      if (!diag) {
        continue;
      }

      const uriKey = this.resolveUri(orphan.source_file, repoRoot);
      if (!uriKey) {
        continue;
      }

      const list = byFile.get(uriKey) ?? [];
      list.push(diag);
      byFile.set(uriKey, list);
    }

    for (const [uriStr, diags] of byFile) {
      this.collection.set(vscode.Uri.file(uriStr), diags);
    }
  }

  scheduledRefresh(repoRoot?: string): void {
    if (this.debounceHandle !== undefined) {
      clearTimeout(this.debounceHandle);
    }
    this.debounceHandle = setTimeout(() => {
      this.debounceHandle = undefined;
      this.refresh(repoRoot);
    }, DEBOUNCE_MS);
  }

  dispose(): void {
    if (this.debounceHandle !== undefined) {
      clearTimeout(this.debounceHandle);
    }
    this.collection.dispose();
  }

  private toDiagnostic(orphan: OrphanRecord): vscode.Diagnostic | null {
    if (!orphan.source_file) {
      return null;
    }

    const range = new vscode.Range(0, 0, 0, 0);
    const message = `[Strata] Orphan ${orphan.kind} '${orphan.name}': ${orphan.reason}`;
    const diag = new vscode.Diagnostic(range, message, vscode.DiagnosticSeverity.Warning);
    diag.source = 'Strata Governance';
    return diag;
  }

  private resolveUri(sourceFile: string | null, repoRoot?: string): string | null {
    if (!sourceFile) {
      return null;
    }

    if (path.isAbsolute(sourceFile)) {
      return sourceFile;
    }

    const root =
      repoRoot ?? vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!root) {
      return null;
    }

    return path.join(root, sourceFile);
  }
}
