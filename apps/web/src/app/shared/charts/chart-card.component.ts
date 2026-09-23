import { Component, Input } from '@angular/core';
import { EChartsOption } from 'echarts';
import { NgxEchartsDirective, provideEcharts } from 'ngx-echarts';
import {
  describePublishedSeries,
  formatPublishedValue,
  humanizeHomologation,
  humanizeUnit,
  humanizeValueKind,
  PublishedSeriesReading,
  publishedYearSpan,
} from '../presentation/official-labels';
import { buildChartOptions } from './chart-options';

export interface ChartSeriesInput {
  name: string;
  points: { x: string; y: number }[];
}

@Component({
  selector: 'app-chart-card',
  standalone: true,
  imports: [NgxEchartsDirective],
  providers: [provideEcharts()],
  host: {
    '[class.evolution]': 'chartType === "line"',
  },
  template: `
    <article class="chart-card">
      <header class="head">
        <div>
          <h2>{{ title }}</h2>
          <p class="summary">{{ summary }}</p>
          <p class="meta">
            {{ measure }} · {{ humanizeUnit(unit) }}
            @if (period) {
              · período {{ period }}
            }
            @if (source) {
              · {{ source }}
            }
            @if (quality) {
              · {{ quality }}
            }
            · {{ humanizeHomologation(homologation) }}
          </p>
        </div>
        @if (yearSpan) {
          <p class="span">{{ yearSpan }}</p>
        }
      </header>
      <div class="body">
        <div
          echarts
          [options]="options"
          class="canvas"
          role="img"
          [attr.aria-label]="summary"
        ></div>
        @if (reading) {
          <aside class="reading" aria-label="Leitura da série">
            <h3>Leitura da série</h3>
            <p>
              <span>Início {{ reading.openingLabel }}</span>
              <strong class="tabular">{{ reading.openingValue }}</strong>
            </p>
            @if (reading.closingLabel) {
              <p>
                <span>Fim {{ reading.closingLabel }}</span>
                <strong class="tabular">{{ reading.closingValue }}</strong>
              </p>
              <p>
                <span>Variação publicada</span>
                <strong class="tabular">{{ reading.change }}</strong>
              </p>
            }
            <p class="note">{{ reading.note }}</p>
          </aside>
        }
      </div>
      <h3 class="table-title">Valores publicados</h3>
      <table>
        <caption class="sr">
          Tabela alternativa de {{ title }}
        </caption>
        <thead>
          <tr>
            <th scope="col">{{ reading ? 'Ano' : 'Categoria' }}</th>
            <th scope="col">{{ seriesName }}</th>
            @if (reading) {
              <th scope="col">Variação em relação ao ano anterior</th>
            }
          </tr>
        </thead>
        <tbody>
          @if (reading) {
            @for (step of reading.steps; track step.label) {
              <tr>
                <th scope="row">{{ step.label }}</th>
                <td class="tabular">{{ step.value }}</td>
                <td class="tabular">{{ step.change }}</td>
              </tr>
            }
          } @else {
            @for (row of rows; track row.x) {
              <tr>
                <th scope="row">{{ row.x }}</th>
                <td class="tabular">{{ formatPublishedValue(row.y, unit) }}</td>
              </tr>
            }
          }
        </tbody>
      </table>
    </article>
  `,
  styles: `
    .chart-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1rem;
      box-shadow: var(--shadow);
    }
    .head {
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      align-items: flex-start;
    }
    h2 {
      margin: 0;
      font-size: 1.05rem;
      color: var(--primary-900);
    }
    p {
      margin: 0.35rem 0 0;
    }
    .summary {
      color: var(--muted);
      font-size: 0.82rem;
    }
    .meta {
      color: var(--muted);
      font-size: 0.82rem;
    }
    .span {
      margin: 0;
      color: var(--muted);
      font-size: 0.92rem;
      white-space: nowrap;
    }
    .body {
      margin-top: 0.75rem;
    }
    :host(.evolution) .body {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 17rem;
      gap: 1rem;
      align-items: start;
    }
    .canvas {
      height: 280px;
    }
    :host(.evolution) .canvas {
      height: 380px;
    }
    .reading {
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 0.85rem;
      background: var(--surface);
    }
    .reading h3,
    .table-title {
      margin: 0;
      font-size: 0.95rem;
      color: var(--primary-900);
    }
    .reading p {
      display: flex;
      flex-direction: column;
      gap: 0.15rem;
      margin-top: 0.75rem;
    }
    .reading span,
    .note {
      color: var(--muted);
      font-size: 0.8rem;
    }
    .reading strong {
      font-size: 1rem;
      color: var(--primary-900);
    }
    .table-title {
      margin-top: 1rem;
    }
    @media (max-width: 800px) {
      :host(.evolution) .body {
        grid-template-columns: 1fr;
      }
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 0.75rem;
      font-size: 0.9rem;
    }
    th,
    td {
      border-bottom: 1px solid var(--border);
      text-align: left;
      padding: 0.35rem 0.25rem;
    }
    .sr {
      position: absolute;
      width: 1px;
      height: 1px;
      overflow: hidden;
      clip: rect(0 0 0 0);
    }
  `,
})
export class ChartCardComponent {
  @Input({ required: true }) title = '';
  @Input({ required: true }) summary = '';
  @Input() set unit(value: string) {
    this.measureUnit = value || '';
    this.redraw();
  }
  get unit(): string {
    return this.measureUnit;
  }
  @Input() period = '';
  @Input() valueKind = '';
  @Input() source = '';
  @Input() quality = '';
  @Input() homologation = '';
  @Input() set chartType(value: 'line' | 'bar') {
    this.kind = value;
    this.redraw();
  }
  get chartType(): 'line' | 'bar' {
    return this.kind;
  }
  @Input() seriesName = 'Série';
  readonly humanizeUnit = humanizeUnit;
  readonly humanizeHomologation = humanizeHomologation;
  readonly formatPublishedValue = formatPublishedValue;

  get measure(): string {
    return humanizeValueKind(this.valueKind);
  }

  rows: { x: string; y: number }[] = [];
  options: EChartsOption = {};
  yearSpan = '';
  reading: PublishedSeriesReading | null = null;
  private kind: 'line' | 'bar' = 'bar';
  private measureUnit = '';

  @Input() set series(value: ChartSeriesInput | null) {
    this.seriesName = value?.name || this.seriesName;
    this.rows = value?.points || [];
    this.redraw();
  }

  private redraw(): void {
    this.yearSpan = this.kind === 'line' ? publishedYearSpan(this.rows) : '';
    this.reading = this.kind === 'line' ? describePublishedSeries(this.rows, this.unit) : null;
    this.options = buildChartOptions({
      chartType: this.kind,
      seriesName: this.seriesName,
      points: this.rows,
      unit: this.unit,
    });
  }
}
