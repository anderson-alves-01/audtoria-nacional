import { Injectable, signal } from '@angular/core';

export interface WorkspaceTab {
  path: string;
  label: string;
  pinned: boolean;
}

const STORAGE_KEY = 'sirta.workspaceTabs';
const MAX_LOOSE_TABS = 6;

/** Paineis abertos na area de trabalho. Ficam na sessao do navegador; nao guardam dado fiscal. */
@Injectable({ providedIn: 'root' })
export class WorkspaceTabsService {
  readonly tabs = signal<WorkspaceTab[]>(this.restore());

  visit(path: string, label: string): void {
    const current = this.tabs();
    const known = current.find((tab) => tab.path === path);
    if (known) {
      if (known.label !== label) {
        this.commit(current.map((tab) => (tab.path === path ? { ...tab, label } : tab)));
      }
      return;
    }
    const next = [...current, { path, label, pinned: false }];
    this.commit(this.trim(next, path));
  }

  togglePin(path: string): void {
    this.commit(this.tabs().map((tab) => (tab.path === path ? { ...tab, pinned: !tab.pinned } : tab)));
  }

  /** Fecha a aba e devolve o endereco para onde seguir, ou null se a aba fechada nao era a atual. */
  close(path: string, currentPath: string): string | null {
    const remaining = this.tabs().filter((tab) => tab.path !== path);
    this.commit(remaining);
    if (path !== currentPath) {
      return null;
    }
    return remaining.length > 0 ? remaining[remaining.length - 1].path : '/visao';
  }

  private trim(tabs: WorkspaceTab[], keep: string): WorkspaceTab[] {
    const loose = tabs.filter((tab) => !tab.pinned);
    let excess = loose.length - MAX_LOOSE_TABS;
    if (excess <= 0) {
      return tabs;
    }
    return tabs.filter((tab) => {
      if (tab.pinned || tab.path === keep || excess <= 0) {
        return true;
      }
      excess -= 1;
      return false;
    });
  }

  private commit(next: WorkspaceTab[]): void {
    this.tabs.set(next);
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      /* sem armazenamento: as abas valem so nesta carga */
    }
  }

  private restore(): WorkspaceTab[] {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return [];
      }
      const parsed = JSON.parse(raw) as WorkspaceTab[];
      return parsed.filter(
        (tab) => typeof tab.path === 'string' && typeof tab.label === 'string' && tab.path.startsWith('/'),
      );
    } catch {
      return [];
    }
  }
}
