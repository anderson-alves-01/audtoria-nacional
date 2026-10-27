import { Component, EventEmitter, Input, Output, computed, signal } from '@angular/core';
import { HEX_LAYOUT } from '../atlas/hex-layout';
import { Measure, bounds, formatMeasure, hexShapes, intensity } from './sped-logic';

/**
 * Mapa de hexágonos por UF. A posição de cada UF é a constante cartográfica do template.
 * UF sem valor fica vazia e nunca recebe cor de zero.
 */
@Component({
  selector: 'app-sped-hex-map',
  standalone: true,
  template: `
    <figure class="hex">
      <div class="bar">
        <figcaption>{{ caption }}</figcaption>
        <button type="button" class="mini" [attr.aria-pressed]="showTable()" (click)="showTable.set(!showTable())">
          {{ showTable() ? 'Ver mapa' : 'Ver tabela' }}
        </button>
      </div>
      @if (!showTable()) {
        <svg viewBox="-40 -48 545 420" role="group" [attr.aria-label]="caption + '. Use Ver tabela para ler os valores.'">
          @for (shape of shapes; track shape.cell.uf) {
            <g
              class="cell"
              [class.selected]="selected === shape.cell.uf"
              [class.empty]="values.get(shape.cell.uf) === null || values.get(shape.cell.uf) === undefined"
              tabindex="0"
              role="button"
              [attr.aria-pressed]="selected === shape.cell.uf"
              [attr.aria-label]="shape.cell.nome + ': ' + text(shape.cell.uf)"
              (click)="picked.emit(shape.cell.uf)"
              (keydown.enter)="picked.emit(shape.cell.uf)"
              (keydown.space)="picked.emit(shape.cell.uf); $event.preventDefault()"
            >
              <title>{{ shape.cell.nome }}: {{ text(shape.cell.uf) }}</title>
              <path [attr.d]="shape.path" [style.fill]="fill(shape.cell.uf)" />
              <text [attr.x]="shape.cx" [attr.y]="shape.cy + 4" text-anchor="middle">{{ shape.cell.uf }}</text>
            </g>
          }
        </svg>
        <p class="scale">
          @if (range(); as r) {
            <span>menor {{ format(r.min) }}</span>
            <span class="ramp" aria-hidden="true" [attr.data-tone]="tone"></span>
            <span>maior {{ format(r.max) }}</span>
          } @else {
            <span>Sem valor neste recorte.</span>
          }
          <span class="none">Hexágono vazio: sem valor gravado.</span>
        </p>
      } @else {
        <div class="table-wrap">
          <table>
            <caption class="sr">{{ caption }}</caption>
            <thead>
              <tr>
                <th scope="col">UF</th>
                <th scope="col">Estado</th>
                <th scope="col" class="num">{{ measure === 'valor' ? 'Valor estimado' : 'Quantidade' }}</th>
              </tr>
            </thead>
            <tbody>
              @for (cell of cells; track cell.uf) {
                <tr>
                  <th scope="row">{{ cell.uf }}</th>
                  <td>{{ cell.nome }}</td>
                  <td class="num tabular">{{ text(cell.uf) }}</td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
    </figure>
  `,
  styles: `
    .hex {
      margin: 0;
    }
    .bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: var(--sp-3);
      margin-bottom: var(--sp-2);
    }
    figcaption {
      color: var(--text-2);
      font-size: 0.78rem;
    }
    .mini {
      min-height: 26px;
      padding: 0 var(--sp-3);
      font-size: 0.78rem;
      background: transparent;
    }
    svg {
      width: 100%;
      max-height: 22rem;
    }
    .cell {
      cursor: pointer;
      outline: none;
    }
    .cell path {
      stroke: var(--surface);
      stroke-width: 2;
    }
    .cell.empty path {
      fill: var(--null-fill);
    }
    .cell text {
      fill: var(--text);
      font-size: 11px;
      font-weight: 600;
      pointer-events: none;
    }
    .cell:hover path,
    .cell:focus-visible path {
      stroke: var(--text);
    }
    .cell.selected path {
      stroke: var(--text);
      stroke-width: 3;
    }
    .scale {
      display: flex;
      flex-wrap: wrap;
      gap: var(--sp-3);
      align-items: center;
      margin: var(--sp-2) 0 0;
      color: var(--muted);
      font-size: 0.78rem;
    }
    .ramp {
      width: 6rem;
      height: 0.55rem;
      border-radius: 99px;
      background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 12%, var(--null-fill)), var(--accent));
    }
    .ramp[data-tone='warn'] {
      background: linear-gradient(90deg, color-mix(in srgb, var(--warn) 12%, var(--null-fill)), var(--warn));
    }
    .none {
      margin-left: auto;
    }
    .table-wrap {
      max-height: 22rem;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: var(--r-sm);
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th,
    td {
      text-align: left;
      padding: 0.3rem 0.6rem;
      border-bottom: 1px solid var(--line);
      font-size: 0.82rem;
    }
    .num {
      text-align: right;
    }
  `,
})
export class SpedHexMapComponent {
  readonly cells = HEX_LAYOUT;
  readonly shapes = hexShapes();
  readonly showTable = signal(false);
  private readonly data = signal<Map<string, number | null>>(new Map());

  @Input({ required: true }) set input(value: Map<string, number | null>) {
    this.data.set(value);
  }
  @Input() caption = '';
  @Input() measure: Measure = 'quantidade';
  @Input() selected: string | null = null;
  @Input() tone: 'accent' | 'warn' = 'accent';
  @Output() picked = new EventEmitter<string>();

  readonly range = computed(() => bounds(this.data().values()));

  get values(): Map<string, number | null> {
    return this.data();
  }

  format(value: number): string {
    return formatMeasure(value, this.measure);
  }

  text(uf: string): string {
    return formatMeasure(this.data().get(uf) ?? null, this.measure);
  }

  fill(uf: string): string | null {
    const range = this.range();
    const value = this.data().get(uf) ?? null;
    if (!range || value === null) {
      return null;
    }
    const level = intensity(value, range.min, range.max) ?? 0;
    const percent = Math.round(18 + level * 82);
    return `color-mix(in srgb, var(--${this.tone}) ${percent}%, var(--null-fill))`;
  }
}
