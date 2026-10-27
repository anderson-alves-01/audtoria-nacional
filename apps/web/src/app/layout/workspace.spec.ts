import { TestBed } from '@angular/core/testing';
import { CommandPaletteComponent } from './command-palette.component';
import { WorkspaceTabsService } from './workspace-tabs.service';

describe('workspace tabs', () => {
  beforeEach(() => sessionStorage.removeItem('sirta.workspaceTabs'));

  it('opens a tab once, keeps pinned tabs and caps the loose ones', () => {
    const tabs = TestBed.inject(WorkspaceTabsService);
    tabs.visit('/visao', 'Visão geral');
    tabs.visit('/visao', 'Visão geral');
    expect(tabs.tabs().length).toBe(1);
    tabs.togglePin('/visao');
    for (let i = 0; i < 9; i += 1) {
      tabs.visit(`/p${i}`, `Painel ${i}`);
    }
    const paths = tabs.tabs().map((tab) => tab.path);
    expect(paths).toContain('/visao');
    expect(paths).toContain('/p8');
    expect(tabs.tabs().filter((tab) => !tab.pinned).length).toBe(6);
  });

  it('returns where to go when the current tab is closed', () => {
    const tabs = TestBed.inject(WorkspaceTabsService);
    tabs.visit('/visao', 'Visão geral');
    tabs.visit('/integracao', 'Entrada e saída');
    expect(tabs.close('/integracao', '/integracao')).toBe('/visao');
    expect(tabs.close('/visao', '/outra')).toBeNull();
  });

  it('survives a reload of the page state', () => {
    TestBed.inject(WorkspaceTabsService).visit('/visao', 'Visão geral');
    const stored = JSON.parse(sessionStorage.getItem('sirta.workspaceTabs') || '[]');
    expect(stored[0].path).toBe('/visao');
  });
});

describe('command palette', () => {
  it('filters, moves with arrows and picks with Enter', () => {
    const fixture = TestBed.createComponent(CommandPaletteComponent);
    const picked: string[] = [];
    fixture.componentInstance.picked.subscribe((id: string) => picked.push(id));
    fixture.componentInstance.items = [
      { id: 'go:/visao', label: 'Visão geral', hint: 'Visão' },
      { id: 'go:/integracao', label: 'Entrada e saída', hint: 'Integração' },
    ];
    fixture.componentInstance.open = true;
    fixture.detectChanges();
    const dialog = fixture.nativeElement.querySelector('[role=dialog]') as HTMLElement;
    expect(dialog).not.toBeNull();
    dialog.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
    dialog.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    expect(picked).toEqual(['go:/integracao']);
    fixture.componentInstance.setQuery('visão');
    fixture.detectChanges();
    expect(fixture.componentInstance.results().length).toBe(1);
  });

  it('closes with Escape', () => {
    const fixture = TestBed.createComponent(CommandPaletteComponent);
    let closed = 0;
    fixture.componentInstance.closed.subscribe(() => (closed += 1));
    fixture.componentInstance.open = true;
    fixture.detectChanges();
    (fixture.nativeElement.querySelector('[role=dialog]') as HTMLElement).dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }),
    );
    expect(closed).toBe(1);
  });
});
