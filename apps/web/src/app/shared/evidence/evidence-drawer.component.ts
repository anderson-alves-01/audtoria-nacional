import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-evidence-drawer',
  standalone: true,
  template: `
    @if (open) {
      <aside class="drawer" role="dialog" aria-label="Evidência e linhagem">
        <div class="head">
          <h2>Evidência</h2>
          <button type="button" (click)="closed.emit()">Fechar</button>
        </div>
        <ng-content />
      </aside>
    }
  `,
  styles: `
    .drawer {
      margin-top: 1rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 4px solid var(--teal-600);
      border-radius: var(--radius);
      padding: 1rem;
    }
    .head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
    }
    h2 {
      margin: 0;
      font-size: 1rem;
      color: var(--primary-900);
    }
    button {
      background: transparent;
      border: 1px solid var(--border);
      border-radius: 8px;
      min-height: 2rem;
      padding: 0 0.7rem;
      cursor: pointer;
    }
  `,
})
export class EvidenceDrawerComponent {
  @Input() open = false;
  @Output() closed = new EventEmitter<void>();
}
