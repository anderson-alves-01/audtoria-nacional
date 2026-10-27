import { Component, ElementRef, EventEmitter, Input, Output, ViewChild, computed, signal } from '@angular/core';

export interface PaletteItem {
  id: string;
  label: string;
  hint: string;
}

/** Paleta de comandos: busca em modulos e acoes, com teclado completo. */
@Component({
  selector: 'app-command-palette',
  standalone: true,
  template: `
    @if (open) {
      <div class="scrim" (click)="closed.emit()" aria-hidden="true"></div>
      <div class="palette" role="dialog" aria-modal="true" aria-label="Paleta de comandos" (keydown)="onKey($event)">
        <input
          #field
          type="text"
          role="combobox"
          aria-expanded="true"
          aria-controls="palette-list"
          aria-autocomplete="list"
          [attr.aria-activedescendant]="active() >= 0 ? 'palette-item-' + active() : null"
          placeholder="Buscar módulo ou ação"
          [value]="query()"
          (input)="setQuery($any($event.target).value)"
        />
        <ul id="palette-list" role="listbox" aria-label="Resultados">
          @for (item of results(); track item.id; let i = $index) {
            <li
              role="option"
              [id]="'palette-item-' + i"
              [attr.aria-selected]="i === active()"
              [class.is-active]="i === active()"
              (mouseenter)="active.set(i)"
              (click)="pick(item)"
            >
              <span>{{ item.label }}</span>
              <small>{{ item.hint }}</small>
            </li>
          }
          @if (results().length === 0) {
            <li class="none" role="presentation">Nada encontrado para esta busca.</li>
          }
        </ul>
        <p class="keys"><kbd>↑</kbd> <kbd>↓</kbd> navegar · <kbd>Enter</kbd> abrir · <kbd>Esc</kbd> fechar</p>
      </div>
    }
  `,
  styles: `
    .scrim {
      position: fixed;
      inset: 0;
      background: rgba(3, 8, 18, 0.6);
      z-index: 60;
    }
    .palette {
      position: fixed;
      z-index: 61;
      top: 14vh;
      left: 50%;
      transform: translateX(-50%);
      width: min(36rem, calc(100vw - 2rem));
      background: var(--surface);
      border: 1px solid var(--line-strong);
      border-radius: var(--r-lg);
      box-shadow: var(--shadow-2);
      overflow: hidden;
    }
    input {
      width: 100%;
      border: 0;
      border-bottom: 1px solid var(--line);
      border-radius: 0;
      min-height: 48px;
      padding: 0 var(--sp-4);
      font-size: 1rem;
      background: transparent;
    }
    input:focus-visible {
      box-shadow: none;
    }
    ul {
      list-style: none;
      margin: 0;
      padding: var(--sp-2);
      max-height: 22rem;
      overflow: auto;
    }
    li {
      display: flex;
      justify-content: space-between;
      gap: var(--sp-3);
      padding: var(--sp-2) var(--sp-3);
      border-radius: var(--r-sm);
      cursor: pointer;
    }
    li.is-active {
      background: var(--accent-soft);
      outline: 1px solid var(--accent);
    }
    li small {
      color: var(--muted);
    }
    .none {
      color: var(--muted);
      cursor: default;
    }
    .keys {
      margin: 0;
      padding: var(--sp-2) var(--sp-4);
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 0.74rem;
    }
    kbd {
      background: var(--surface-3);
      border: 1px solid var(--line-strong);
      border-radius: 4px;
      padding: 0 4px;
    }
  `,
})
export class CommandPaletteComponent {
  @Input() set items(value: PaletteItem[]) {
    this.all.set(value);
  }
  @Input() set open(value: boolean) {
    this.isOpen = value;
    if (value) {
      this.query.set('');
      this.active.set(0);
      setTimeout(() => this.field?.nativeElement.focus());
    }
  }
  get open(): boolean {
    return this.isOpen;
  }
  @Output() picked = new EventEmitter<string>();
  @Output() closed = new EventEmitter<void>();
  @ViewChild('field') field?: ElementRef<HTMLInputElement>;

  readonly query = signal('');
  readonly active = signal(0);
  private readonly all = signal<PaletteItem[]>([]);
  private isOpen = false;

  readonly results = computed(() => {
    const term = this.query().trim().toLowerCase();
    if (!term) {
      return this.all();
    }
    return this.all().filter(
      (item) => item.label.toLowerCase().includes(term) || item.hint.toLowerCase().includes(term),
    );
  });

  setQuery(value: string): void {
    this.query.set(value);
    this.active.set(0);
  }

  pick(item: PaletteItem): void {
    this.picked.emit(item.id);
  }

  onKey(event: KeyboardEvent): void {
    const count = this.results().length;
    if (event.key === 'Escape') {
      event.preventDefault();
      this.closed.emit();
    } else if (event.key === 'ArrowDown' && count > 0) {
      event.preventDefault();
      this.active.set((this.active() + 1) % count);
    } else if (event.key === 'ArrowUp' && count > 0) {
      event.preventDefault();
      this.active.set((this.active() - 1 + count) % count);
    } else if (event.key === 'Enter' && count > 0) {
      event.preventDefault();
      this.pick(this.results()[this.active()]);
    }
  }
}
