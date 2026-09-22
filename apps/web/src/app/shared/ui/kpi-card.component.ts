import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-kpi-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <article class="kpi-card">
      <p class="kpi-label">{{ label }}</p>
      <p class="kpi-value tabular">{{ value }}</p>
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
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 0.9rem 1rem;
      box-shadow: var(--shadow);
      min-height: 6.5rem;
    }
    .kpi-label,
    .kpi-meta,
    .kpi-kind {
      margin: 0;
      color: var(--muted);
      font-size: 0.82rem;
    }
    .kpi-value {
      margin: 0.35rem 0;
      font-size: 1.45rem;
      font-weight: 700;
      color: var(--primary-900);
    }
  `,
})
export class KpiCardComponent {
  @Input({ required: true }) label = '';
  @Input({ required: true }) value = '';
  @Input() meta = '';
  @Input() kind = '';
}
