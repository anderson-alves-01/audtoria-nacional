import { Component, EventEmitter, Input, Output, computed, signal } from '@angular/core';
import { HEX_LAYOUT, HexCell } from '../atlas/hex-layout';
import { compactPublishedValue } from '../shared/presentation/official-labels';
import {
  EMPTY,
  HexShape,
  Measure,
  bounds,
  formatMeasure,
  hexShapes,
  intensity,
  viewBoxFor,
  visibleShapes,
} from './sped-logic';

/**
 * Mapa de hexágonos por UF com quantidade e valor no mesmo hexágono. A posição de cada UF é a
 * constante cartográfica do template. A cor segue a medida escolhida. UF sem valor fica vazia
 * e nunca recebe cor de zero.
 */
@Component({
  selector: 'app-sped-hex-map',
  standalone: true,
  template: `
    <figure class="hex">
      <div class="bar">
        <figcaption>{{ caption }}</figcaption>
        <span class="actions">
          <span class="mode" role="group" aria-label="Colorir por">
            <span class="lbl">Colorir por</span>
            <button type="button" class="mini" [attr.aria-pressed]="colorBy() === 'quantidade'" (click)="colorBy.set('quantidade')">
              Quantidade
            </button>
            <button type="button" class="mini" [attr.aria-pressed]="colorBy() === 'valor'" (click)="colorBy.set('valor')">
              Valor
            </button>
          </span>
          @if (isolated) {
            <button type="button" class="mini" (click)="cleared.emit()">Mostrar todas as UFs</button>
          }
          <button type="button" class="mini" [attr.aria-pressed]="showTable()" (click)="showTable.set(!showTable())">
            {{ showTable() ? 'Ver mapa' : 'Ver tabela' }}
          </button>
        </span>
      </div>
      @if (!showTable()) {
        <svg
          [attr.viewBox]="viewBox"
          [class.single]="isolated"
          role="group"
          [attr.aria-label]="caption + '. Use Ver tabela para ler os valores.'"
        >
          @for (shape of shown; track shape.cell.uf) {
            <g
              class="cell"
              [class.selected]="selected === shape.cell.uf"
              [class.empty]="isEmpty(shape.cell.uf)"
              tabindex="0"
              role="button"
              [attr.aria-pressed]="selected === shape.cell.uf"
              [attr.aria-label]="label(shape.cell.uf, shape.cell.nome)"
              (click)="picked.emit(shape.cell.uf)"
              (keydown.enter)="picked.emit(shape.cell.uf)"
              (keydown.space)="picked.emit(shape.cell.uf); $event.preventDefault()"
            >
              <title>{{ label(shape.cell.uf, shape.cell.nome) }}</title>
              <path [attr.d]="shape.path" [style.fill]="fill(shape.cell.uf)" />
              <text class="uf" [attr.x]="shape.cx" [attr.y]="shape.cy - 8" text-anchor="middle">{{ shape.cell.uf }}</text>
              <text class="val q" [attr.x]="shape.cx" [attr.y]="shape.cy + 5" text-anchor="middle">{{ compact(shape.cell.uf, 'quantidade') }}</text>
              <text class="val v" [attr.x]="shape.cx" [attr.y]="shape.cy + 15" text-anchor="middle">{{ compact(shape.cell.uf, 'valor') }}</text>
            </g>
          }
        </svg>
        <p class="scale">
          @if (isolated) {
            <span>
              {{ selectedName }}: quantidade {{ text(selected ?? '', 'quantidade') }}, valor {{ text(selected ?? '', 'valor') }}.
              As demais UFs estão ocultas.
            </span>
          } @else {
            @if (range(); as r) {
              <span>{{ colorBy() === 'valor' ? 'Valor' : 'Quantidade' }}: menor {{ format(r.min) }}</span>
              <span class="ramp" aria-hidden="true" [attr.data-tone]="tone"></span>
              <span>maior {{ format(r.max) }}</span>
            } @else {
              <span>Sem valor neste recorte.</span>
            }
          }
          <span class="none">Cada hexágono mostra UF, quantidade e valor. Vazio: sem valor gravado.</span>
        </p>
      } @else {
        <div class="table-wrap">
          <table>
            <caption class="sr">{{ caption }}</caption>
            <thead>
              <tr>
                <th scope="col">UF</th>
                <th scope="col">Estado</th>
                <th scope="col" class="num">Quantidade</th>
                <th scope="col" class="num">Valor</th>
              </tr>
            </thead>
            <tbody>
              @for (cell of tableCells; track cell.uf) {
                <tr>
                  <th scope="row">{{ cell.uf }}</th>
                  <td>{{ cell.nome }}</td>
                  <td class="num tabular">{{ text(cell.uf, 'quantidade') }}</td>
                  <td class="num tabular">{{ text(cell.uf, 'valor') }}</td>
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
      flex-wrap: wrap;
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
    .mini[aria-pressed='true'] {
      border-color: var(--accent);
      color: var(--accent-strong);
    }
    .mode {
      display: inline-flex;
      align-items: center;
      gap: var(--sp-2);
    }
    .lbl {
      color: var(--muted);
      font-size: 0.78rem;
    }
    svg {
      width: 100%;
      max-height: 26rem;
    }
    svg.single {
      max-height: 14rem;
    }
    svg.single .cell.selected path {
      stroke-width: 1.5;
    }
    .actions {
      display: inline-flex;
      flex-wrap: wrap;
      gap: var(--sp-2);
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
      pointer-events: none;
    }
    .cell text.uf {
      font-size: 11px;
      font-weight: 700;
    }
    .cell text.val {
      font-size: 7px;
      font-weight: 500;
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
      max-height: 26rem;
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
  readonly colorBy = signal<Measure>('quantidade');
  private readonly quantityData = signal<Map<string, number | null>>(new Map());
  private readonly valueData = signal<Map<string, number | null>>(new Map());

  @Input({ required: true }) set quantity(value: Map<string, number | null>) {
    this.quantityData.set(value);
  }
  @Input({ required: true }) set value(value: Map<string, number | null>) {
    this.valueData.set(value);
  }
  @Input() caption = '';
  @Input() selected: string | null = null;
  @Output() picked = new EventEmitter<string>();
  @Output() cleared = new EventEmitter<void>();

  /** Quantidade em tom de destaque; valor em tom de aviso, para nao confundir as duas medidas. */
  get tone(): 'accent' | 'warn' {
    return this.colorBy() === 'valor' ? 'warn' : 'accent';
  }

  /** Com UF escolhida e conhecida, so o hexagono dela aparece. */
  get shown(): HexShape[] {
    return visibleShapes(this.shapes, this.selected);
  }

  get isolated(): boolean {
    return this.shown.length === 1;
  }

  get viewBox(): string {
    return viewBoxFor(this.shown);
  }

  get tableCells(): HexCell[] {
    return this.isolated ? this.cells.filter((cell) => cell.uf === this.selected) : this.cells;
  }

  get selectedName(): string {
    return this.cells.find((cell) => cell.uf === this.selected)?.nome ?? '';
  }

  private readonly active = computed(() => (this.colorBy() === 'valor' ? this.valueData() : this.quantityData()));
  readonly range = computed(() => bounds(this.active().values()));

  private mapOf(measure: Measure): Map<string, number | null> {
    return measure === 'valor' ? this.valueData() : this.quantityData();
  }

  isEmpty(uf: string): boolean {
    return (this.active().get(uf) ?? null) === null;
  }

  format(value: number): string {
    return formatMeasure(value, this.colorBy());
  }

  text(uf: string, measure: Measure): string {
    return formatMeasure(this.mapOf(measure).get(uf) ?? null, measure);
  }

  /** Forma curta para caber no hexagono. O valor exato fica na tabela e no rotulo. */
  compact(uf: string, measure: Measure): string {
    const value = this.mapOf(measure).get(uf) ?? null;
    return value === null ? EMPTY : compactPublishedValue(value, measure === 'valor' ? 'BRL' : 'COUNT');
  }

  label(uf: string, name: string): string {
    return `${name}: quantidade ${this.text(uf, 'quantidade')}, valor ${this.text(uf, 'valor')}`;
  }

  fill(uf: string): string | null {
    const range = this.range();
    const value = this.active().get(uf) ?? null;
    if (!range || value === null) {
      return null;
    }
    const level = intensity(value, range.min, range.max) ?? 0;
    const percent = Math.round(18 + level * 82);
    return `color-mix(in srgb, var(--${this.tone}) ${percent}%, var(--null-fill))`;
  }
}
