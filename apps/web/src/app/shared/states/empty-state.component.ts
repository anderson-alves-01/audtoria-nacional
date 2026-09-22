import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  template: `
    <div class="empty" role="status">
      <h2>{{ title }}</h2>
      <p>{{ reason }}</p>
      @if (hint) {
        <p class="hint">{{ hint }}</p>
      }
      <ng-content />
    </div>
  `,
  styles: `
    .empty {
      background: var(--surface);
      border: 1px dashed var(--border);
      border-radius: var(--radius);
      padding: 1.25rem;
    }
    h2 {
      margin: 0 0 0.5rem;
      color: var(--primary-900);
      font-size: 1.15rem;
    }
    p {
      margin: 0 0 0.5rem;
    }
    .hint {
      color: var(--muted);
    }
  `,
})
export class EmptyStateComponent {
  @Input({ required: true }) title = '';
  @Input({ required: true }) reason = '';
  @Input() hint = '';
}
