import { Component, EventEmitter, Input, Output } from '@angular/core';

export interface FilterChip {
  key: string;
  label: string;
  value: string;
}

/** Filtros ativos como chips removiveis, no estilo das ferramentas de BI. */
@Component({
  selector: 'app-filter-bar',
  standalone: true,
  template: `
    <div class="bar" role="group" [attr.aria-label]="label">
      <span class="title">Filtros</span>
      @if (chips.length === 0) {
        <span class="none">Nenhum filtro ativo. Clique em um gráfico ou escolha um filtro.</span>
      }
      @for (chip of chips; track chip.key) {
        <span class="chip">
          <span class="chip-label">{{ chip.label }}</span>
          <strong>{{ chip.value }}</strong>
          <button type="button" class="chip-x" [attr.aria-label]="'Remover filtro ' + chip.label" (click)="removed.emit(chip.key)">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </button>
        </span>
      }
      @if (chips.length > 1) {
        <button type="button" class="clear" (click)="cleared.emit()">Limpar tudo</button>
      }
    </div>
  `,
  styles: `
    .bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: var(--sp-2);
      padding: var(--sp-2) var(--sp-3);
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--r);
    }
    .title {
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-2);
    }
    .none {
      color: var(--muted);
      font-size: 0.82rem;
    }
    .chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--accent-soft);
      border: 1px solid var(--accent);
      border-radius: 99px;
      padding: 1px 4px 1px 10px;
      font-size: 0.82rem;
    }
    .chip-label {
      color: var(--text-2);
    }
    .chip-x {
      min-height: 22px;
      width: 22px;
      padding: 0;
      border: 0;
      border-radius: 99px;
      background: transparent;
      display: grid;
      place-items: center;
    }
    .chip-x svg {
      width: 12px;
      height: 12px;
      fill: none;
      stroke: currentColor;
      stroke-width: 2;
    }
    .clear {
      min-height: 26px;
      padding: 0 var(--sp-3);
      font-size: 0.8rem;
      background: transparent;
    }
  `,
})
export class FilterBarComponent {
  @Input() chips: FilterChip[] = [];
  @Input() label = 'Filtros ativos';
  @Output() removed = new EventEmitter<string>();
  @Output() cleared = new EventEmitter<void>();
}
