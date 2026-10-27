import { Component, EventEmitter, Input, Output, effect, inject } from '@angular/core';
import { EChartsOption } from 'echarts';
import { NgxEchartsDirective, provideEcharts } from 'ngx-echarts';
import { ThemeService } from '../ui/theme.service';
import { formatPublishedValue } from '../presentation/official-labels';
import {
  BiChartInput,
  alternativeHeaders,
  alternativeRows,
  alternativeUnits,
  buildBiOptions,
} from './bi-chart-options';

export interface ChartPick {
  value: string;
  multi: boolean;
}

/**
 * Grafico de BI: clique seleciona (filtro cruzado), Shift soma selecoes, duplo clique
 * detalha, faixa no eixo seleciona varias categorias e sempre ha uma tabela alternativa.
 */
@Component({
  selector: 'app-bi-chart',
  standalone: true,
  imports: [NgxEchartsDirective],
  providers: [provideEcharts()],
  template: `
    <figure class="bi-chart">
      <div class="bar">
        <figcaption>{{ caption }}</figcaption>
        <button type="button" class="mini" [attr.aria-pressed]="showTable" (click)="showTable = !showTable">
          {{ showTable ? 'Ver gráfico' : 'Ver tabela' }}
        </button>
      </div>
      @if (!showTable) {
        <div
          echarts
          class="canvas"
          [options]="options"
          [style.height.px]="height"
          role="img"
          [attr.aria-label]="caption + '. Use Ver tabela para ler os valores.'"
          (chartClick)="onClick($event)"
          (chartDblClick)="onDblClick($event)"
          (chartBrushSelected)="onBrush($event)"
        ></div>
      } @else {
        <div class="table-wrap">
          <table>
            <caption class="sr">Valores de {{ caption }}</caption>
            <thead>
              <tr>
                <th scope="col">Categoria</th>
                @for (head of headers; track head) {
                  <th scope="col">{{ head }}</th>
                }
              </tr>
            </thead>
            <tbody>
              @for (row of rows; track row.label) {
                <tr>
                  <th scope="row">{{ row.label }}</th>
                  @for (cell of row.values; track $index) {
                    <td class="tabular">{{ format(cell, $index) }}</td>
                  }
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
    </figure>
  `,
  styles: `
    .bi-chart {
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
    .mini[aria-pressed='true'] {
      border-color: var(--accent);
      color: var(--accent-strong);
    }
    .canvas {
      width: 100%;
    }
    .table-wrap {
      max-height: 22rem;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: var(--r-sm);
    }
  `,
})
export class BiChartComponent {
  private readonly themes = inject(ThemeService);
  private spec: BiChartInput | null = null;

  @Input({ required: true }) set input(value: BiChartInput) {
    this.spec = value;
    this.refresh();
  }
  @Input() caption = '';
  @Input() height = 300;
  @Output() picked = new EventEmitter<ChartPick>();
  @Output() drilled = new EventEmitter<string>();
  @Output() brushed = new EventEmitter<string[]>();

  options: EChartsOption = {};
  showTable = false;
  headers: string[] = [];
  units: string[] = [];
  rows: { label: string; values: (number | null)[] }[] = [];

  constructor() {
    effect(() => {
      this.themes.theme();
      queueMicrotask(() => this.refresh());
    });
  }

  format(value: number | null, column = 0): string {
    if (value === null || value === undefined) {
      return '—';
    }
    return formatPublishedValue(value, this.units[column] ?? this.spec?.unit ?? '');
  }

  onClick(event: unknown): void {
    const name = this.nameOf(event);
    if (name) {
      const raw = (event as { event?: { event?: MouseEvent } }).event?.event;
      this.picked.emit({ value: name, multi: !!(raw?.shiftKey || raw?.ctrlKey || raw?.metaKey) });
    }
  }

  onDblClick(event: unknown): void {
    const name = this.nameOf(event);
    if (name) {
      this.drilled.emit(name);
    }
  }

  onBrush(event: unknown): void {
    const batch = (event as { batch?: { selected?: { dataIndex?: number[] }[] }[] }).batch?.[0];
    const indexes = batch?.selected?.[0]?.dataIndex ?? [];
    const categories = this.spec?.categories ?? [];
    this.brushed.emit(indexes.map((index) => categories[index]).filter((name): name is string => !!name));
  }

  private nameOf(event: unknown): string {
    const params = event as { name?: string; value?: unknown };
    if (this.spec?.kind === 'heatmap' && Array.isArray(params.value)) {
      return (this.spec.categories ?? [])[Number(params.value[0])] ?? '';
    }
    return params.name ?? '';
  }

  private refresh(): void {
    if (!this.spec) {
      return;
    }
    this.options = buildBiOptions(this.spec);
    this.headers = alternativeHeaders(this.spec);
    this.units = alternativeUnits(this.spec);
    this.rows = alternativeRows(this.spec);
  }
}
