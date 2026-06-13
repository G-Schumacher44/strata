import * as cp from 'child_process';
import * as vscode from 'vscode';

export interface OrphanRecord {
  id: string;
  kind: string;
  name: string;
  source_file: string | null;
  reason: string;
}

export interface StrataResult<T = unknown> {
  ok: boolean;
  data?: T;
  error?: string;
}

export function detectStrata(): boolean {
  try {
    const result = cp.spawnSync('strata', ['--version'], {
      encoding: 'utf-8',
      timeout: 5000,
      shell: false,
    });
    return result.status === 0;
  } catch {
    return false;
  }
}

export function promptInstall(): void {
  vscode.window
    .showErrorMessage(
      'Strata CLI not found on PATH. Install with: pipx install strata',
      'Copy install command'
    )
    .then((choice) => {
      if (choice === 'Copy install command') {
        void vscode.env.clipboard.writeText('pipx install strata');
        void vscode.window.showInformationMessage('Copied: pipx install strata');
      }
    });
}

export function runStrataJSON<T = unknown>(
  args: string[],
  cwd?: string
): StrataResult<T> {
  try {
    const result = cp.spawnSync('strata', args, {
      encoding: 'utf-8',
      timeout: 60000,
      cwd,
      shell: false,
    });

    if (result.error) {
      return { ok: false, error: `spawn error: ${result.error.message}` };
    }

    if (result.status !== 0) {
      const errText = (result.stderr || result.stdout || 'non-zero exit').trim();
      return { ok: false, error: errText };
    }

    const raw = (result.stdout || '').trim();
    if (!raw) {
      return { ok: false, error: 'empty output from strata' };
    }

    const data = JSON.parse(raw) as T;
    return { ok: true, data };
  } catch (err: unknown) {
    return {
      ok: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

export function buildGraph(repoPath: string): StrataResult<Record<string, unknown>> {
  return runStrataJSON<Record<string, unknown>>(['build', '--repo', repoPath, '--json']);
}

export function impactFromScope(
  filePath: string,
  repoPath?: string
): StrataResult<Record<string, unknown>> {
  const args = ['query', 'scope', filePath];
  return runStrataJSON<Record<string, unknown>>(args, repoPath);
}

export function navigateField(
  anchor: string,
  repoPath?: string
): StrataResult<Record<string, unknown>> {
  const args = ['query', 'navigate', anchor, '--json'];
  return runStrataJSON<Record<string, unknown>>(args, repoPath);
}

export function queryOrphans(repoPath?: string): StrataResult<OrphanRecord[]> {
  const args = ['query', 'orphans', '--kind', 'all'];
  return runStrataJSON<OrphanRecord[]>(args, repoPath);
}

export function resolveRepoPath(): string | undefined {
  const config = vscode.workspace.getConfiguration('strata');
  const configured = config.get<string>('repoPath');
  if (configured && configured.trim()) {
    return configured.trim();
  }
  return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
}
