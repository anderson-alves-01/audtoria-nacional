import { Component, EventEmitter, Input, Output } from '@angular/core';

export interface TabItem {
  id: string;
  label: string;
  count?: number | null;
}

/** Abas com teclado (setas, Home, End) e papel tablist. O conteudo fica a cargo da tela. */
@Component({
  selector: 'app-tabs',
  standalone: true,
  template: `
    <div class="tabs" role="tablist" [attr.aria-label]="label" (keydown)="onKey($event)">
      @for (tab of tabs; track tab.id) {
        <button
          type="button"
          role="tab"
          class="tab"
          [id]="'tab-' + tab.id"
          [attr.aria-selected]="tab.id === active"
          [attr.aria-controls]="'panel-' + tab.id"
          [attr.tabindex]="tab.id === active ? 0 : -1"
          (click)="select(tab.id)"
        >
          {{ tab.label }}
          @if (tab.count !== undefined && tab.count !== null) {
            <span class="count tabular">{{ tab.count }}</span>
          }
        </button>
      }
    </div>
  `,
  styles: `
    .tabs {
      display: flex;
      gap: var(--sp-1);
      border-bottom: 1px solid var(--line);
      overflow-x: auto;
    }
    .tab {
      background: transparent;
      border: 0;
      border-bottom: 2px solid transparent;
      border-radius: 0;
      color: var(--text-2);
      min-height: 38px;
      padding: 0 var(--sp-4);
      white-space: nowrap;
    }
    .tab:hover:not(:disabled) {
      background: var(--surface-2);
    }
    .tab[aria-selected='true'] {
      color: var(--accent-strong);
      border-bottom-color: var(--accent);
      font-weight: 600;
    }
    .count {
      margin-left: 6px;
      font-size: 0.72rem;
      background: var(--surface-3);
      border-radius: 99px;
      padding: 0 6px;
    }
  `,
})
export class TabsComponent {
  @Input({ required: true }) tabs: TabItem[] = [];
  @Input({ required: true }) active = '';
  @Input() label = 'Abas';
  @Output() activeChange = new EventEmitter<string>();

  select(id: string): void {
    if (id !== this.active) {
      this.active = id;
      this.activeChange.emit(id);
    }
  }

  onKey(event: KeyboardEvent): void {
    const index = this.tabs.findIndex((tab) => tab.id === this.active);
    let next = index;
    if (event.key === 'ArrowRight') {
      next = (index + 1) % this.tabs.length;
    } else if (event.key === 'ArrowLeft') {
      next = (index - 1 + this.tabs.length) % this.tabs.length;
    } else if (event.key === 'Home') {
      next = 0;
    } else if (event.key === 'End') {
      next = this.tabs.length - 1;
    } else {
      return;
    }
    event.preventDefault();
    this.select(this.tabs[next].id);
    queueMicrotask(() => document.getElementById('tab-' + this.tabs[next].id)?.focus());
  }
}
