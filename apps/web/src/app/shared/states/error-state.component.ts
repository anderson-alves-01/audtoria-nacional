import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-error-state',
  standalone: true,
  template: `
    <div class="error" role="alert">
      <h2>{{ title }}</h2>
      <p>{{ message }}</p>
      @if (correlationId) {
        <p class="meta">Identificador {{ correlationId }}</p>
      }
      @if (retry) {
        <button type="button" (click)="retried.emit()">Tentar novamente</button>
      }
    </div>
  `,
  styles: `
    .error {
      background: var(--danger-soft);
      border: 1px solid var(--danger);
      border-radius: var(--r);
      padding: var(--sp-4);
    }
    h2 {
      margin: 0 0 var(--sp-2);
      color: var(--danger);
      font-size: 1rem;
    }
    p {
      margin: 0 0 var(--sp-2);
    }
    .meta {
      color: var(--muted);
      font-size: 0.82rem;
    }
  `,
})
export class ErrorStateComponent {
  @Input() title = 'Falha ao carregar';
  @Input({ required: true }) message = '';
  @Input() correlationId = '';
  @Input() retry = false;
  @Output() retried = new EventEmitter<void>();
}
