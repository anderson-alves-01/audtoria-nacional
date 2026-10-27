import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

/** Indicador de painel: valor publicado, contexto e, se houver, a serie curta ao lado. */
@Component({
  selector: 'app-kpi-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <article class="kpi-card" [attr.data-tone]="tone">
      <p class="kpi-label">{{ label }}</p>
      <div class="kpi-row">
        <p class="kpi-value tabular">{{ value }}</p>
        @if (sparkPath) {
          <svg class="spark" viewBox="0 0 100 28" aria-hidden="true" preserveAspectRatio="none">
            <path [attr.d]="sparkPath" />
          </svg>
        }
      </div>
      @if (delta) {
        <p class="kpi-delta tabular">{{ delta }}</p>
      }
      @if (meta) {
        <p class="kpi-meta">{{ meta }}</p>
      }
      @if (kind) {
        <p class="kpi-kind">{{ kind }}</p>
      }
    </article>
  `,
  styles: `
    .kpi-card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-left: 3px solid var(--accent);
      border-radius: var(--r);
      padding: var(--sp-3) var(--sp-4);
      box-shadow: var(--shadow-1);
      min-height: 6.5rem;
    }
    .kpi-card[data-tone='warn'] {
      border-left-color: var(--warn);
    }
    .kpi-card[data-tone='danger'] {
      border-left-color: var(--danger);
    }
    .kpi-card[data-tone='info'] {
      border-left-color: var(--info);
    }
    .kpi-label,
    .kpi-meta,
    .kpi-kind,
    .kpi-delta {
      margin: 0;
      color: var(--muted);
      font-size: 0.78rem;
    }
    .kpi-label {
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 600;
      color: var(--text-2);
    }
    .kpi-row {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: var(--sp-3);
    }
    .kpi-value {
      margin: var(--sp-2) 0;
      font-size: 1.6rem;
      font-weight: 600;
      color: var(--text);
    }
    .spark {
      width: 5.5rem;
      height: 1.75rem;
      flex: none;
      margin-bottom: var(--sp-2);
    }
    .spark path {
      fill: none;
      stroke: var(--accent);
      stroke-width: 2;
      vector-effect: non-scaling-stroke;
    }
    .kpi-kind {
      margin-top: var(--sp-1);
      color: var(--warn);
    }
  `,
})
export class KpiCardComponent {
  @Input({ required: true }) label = '';
  @Input({ required: true }) value = '';
  @Input() meta = '';
  @Input() kind = '';
  @Input() delta = '';
  @Input() tone: 'accent' | 'warn' | 'danger' | 'info' = 'accent';
  /** Serie curta ja publicada. Valores nulos ficam de fora; sem dois pontos nao ha linha. */
  @Input() set spark(values: (number | null)[] | null) {
    this.sparkPath = buildSparkPath(values ?? []);
  }
  sparkPath = '';
}

export function buildSparkPath(values: (number | null)[]): string {
  const real = values.filter((entry): entry is number => typeof entry === 'number' && Number.isFinite(entry));
  if (real.length < 2) {
    return '';
  }
  const min = Math.min(...real);
  const max = Math.max(...real);
  const span = max - min || 1;
  const step = 100 / (real.length - 1);
  return real
    .map((entry, index) => {
      const x = (index * step).toFixed(2);
      const y = (26 - ((entry - min) / span) * 24).toFixed(2);
      return `${index === 0 ? 'M' : 'L'}${x} ${y}`;
    })
    .join(' ');
}
