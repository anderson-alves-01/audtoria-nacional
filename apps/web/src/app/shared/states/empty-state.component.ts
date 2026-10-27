import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  template: `
    <div class="empty" role="status">
      <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M4 19V5M4 19h16M8 15v-4M12 15V8M16 15v-6" />
      </svg>
      <div>
        <h2>{{ title }}</h2>
        <p>{{ reason }}</p>
        @if (hint) {
          <p class="hint">{{ hint }}</p>
        }
        <ng-content />
      </div>
    </div>
  `,
  styles: `
    .empty {
      display: flex;
      gap: var(--sp-4);
      background: var(--surface);
      border: 1px dashed var(--line-strong);
      border-radius: var(--r);
      padding: var(--sp-5);
    }
    .icon {
      width: 2rem;
      height: 2rem;
      flex: none;
      fill: none;
      stroke: var(--accent);
      stroke-width: 1.6;
      stroke-linecap: round;
    }
    h2 {
      margin: 0 0 var(--sp-2);
      font-size: 1.05rem;
    }
    p {
      margin: 0 0 var(--sp-2);
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
