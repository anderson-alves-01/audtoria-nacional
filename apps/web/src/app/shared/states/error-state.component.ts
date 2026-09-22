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
      background: #fff6f7;
      border: 1px solid #f0c9ce;
      border-radius: var(--radius);
      padding: 1rem 1.1rem;
    }
    h2 {
      margin: 0 0 0.4rem;
      color: var(--red-600);
      font-size: 1.1rem;
    }
    p {
      margin: 0 0 0.4rem;
    }
    .meta {
      color: var(--muted);
      font-size: 0.85rem;
    }
    button {
      margin-top: 0.4rem;
      background: var(--primary-900);
      color: #fff;
      border: 0;
      border-radius: 8px;
      min-height: 2.25rem;
      padding: 0 0.8rem;
      cursor: pointer;
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
