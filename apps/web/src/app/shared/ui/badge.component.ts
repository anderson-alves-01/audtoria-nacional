import { Component, Input } from '@angular/core';

/** Selo curto de estado, fonte ou frescor. A cor nunca e a unica informacao: sempre ha texto. */
@Component({
  selector: 'app-badge',
  standalone: true,
  template: `<span class="badge" [attr.data-tone]="tone"><ng-content /></span>`,
  styles: `
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 1px 8px;
      border-radius: 99px;
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.02em;
      background: var(--surface-3);
      color: var(--text-2);
      border: 1px solid var(--line-strong);
      white-space: nowrap;
    }
    .badge[data-tone='accent'] {
      background: var(--accent-soft);
      color: var(--accent-strong);
      border-color: transparent;
    }
    .badge[data-tone='ok'] {
      background: var(--ok-soft);
      color: var(--ok);
      border-color: transparent;
    }
    .badge[data-tone='warn'] {
      background: var(--warn-soft);
      color: var(--warn);
      border-color: transparent;
    }
    .badge[data-tone='danger'] {
      background: var(--danger-soft);
      color: var(--danger);
      border-color: transparent;
    }
    .badge[data-tone='info'] {
      background: var(--info-soft);
      color: var(--info);
      border-color: transparent;
    }
  `,
})
export class BadgeComponent {
  @Input() tone: 'neutral' | 'accent' | 'ok' | 'warn' | 'danger' | 'info' = 'neutral';
}
