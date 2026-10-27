import { Component, Input } from '@angular/core';

/** Painel de BI: titulo, contexto (fonte, competencia), acoes e conteudo. */
@Component({
  selector: 'app-panel',
  standalone: true,
  template: `
    <section class="panel" [attr.aria-labelledby]="titleId">
      <header class="panel-head">
        <div class="panel-titles">
          <h2 [id]="titleId">{{ title }}</h2>
          @if (subtitle) {
            <p class="panel-sub">{{ subtitle }}</p>
          }
        </div>
        <div class="panel-actions">
          <ng-content select="[panelActions]" />
        </div>
      </header>
      <div class="panel-body">
        <ng-content />
      </div>
      @if (source) {
        <footer class="panel-foot">{{ source }}</footer>
      }
    </section>
  `,
  styles: `
    .panel {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--r);
      box-shadow: var(--shadow-1);
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .panel-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: var(--sp-3);
      padding: var(--sp-3) var(--sp-4);
      border-bottom: 1px solid var(--line);
    }
    h2 {
      margin: 0;
      font-size: 0.95rem;
    }
    .panel-sub {
      margin: 2px 0 0;
      color: var(--muted);
      font-size: 0.78rem;
    }
    .panel-actions {
      display: flex;
      gap: var(--sp-2);
      align-items: center;
    }
    .panel-body {
      padding: var(--sp-4);
      min-width: 0;
    }
    .panel-foot {
      padding: var(--sp-2) var(--sp-4);
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 0.74rem;
    }
  `,
})
export class PanelComponent {
  @Input({ required: true }) title = '';
  @Input() subtitle = '';
  @Input() source = '';
  private static seq = 0;
  readonly titleId = `panel-title-${PanelComponent.seq++}`;
}
