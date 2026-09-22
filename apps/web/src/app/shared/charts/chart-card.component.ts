import { Component, Input } from '@angular/core';
import { EChartsOption } from 'echarts';
import { NgxEchartsDirective, provideEcharts } from 'ngx-echarts';

export interface ChartSeriesInput {
  name: string;
  points: { x: string; y: number }[];
}

@Component({
  selector: 'app-chart-card',
  standalone: true,
  imports: [NgxEchartsDirective],
  providers: [provideEcharts()],
  template: `
    <article class="chart-card">
      <header>
        <h2>{{ title }}</h2>
        <p>{{ summary }}</p>
        <p class="meta">
          Unidade {{ unit }} · período {{ period || 'não informado' }} · {{ valueKind }}
          @if (source) {
            · fonte {{ source }}
          }
          @if (quality) {
            · qualidade {{ quality }}
          }
          @if (homologation) {
            · homologação {{ homologation }}
          }
        </p>
      </header>
      <div
        echarts
        [options]="options"
        class="canvas"
        role="img"
        [attr.aria-label]="summary"
      ></div>
      <table>
        <caption class="sr">
          Tabela alternativa de {{ title }}
        </caption>
        <thead>
          <tr>
            <th scope="col">Categoria</th>
            <th scope="col">{{ seriesName }}</th>
          </tr>
        </thead>
        <tbody>
          @for (row of rows; track row.x) {
            <tr>
              <th scope="row">{{ row.x }}</th>
              <td class="tabular">{{ row.y }}</td>
            </tr>
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
    h2 {
      margin: 0;
      font-size: 1.05rem;
      color: var(--primary-900);
    }
    p {
      margin: 0.35rem 0 0;
    }
    .meta {
      color: var(--muted);
      font-size: 0.82rem;
    }
    .canvas {
      height: 280px;
      margin-top: 0.75rem;
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
  @Input() unit = '';
  @Input() period = '';
  @Input() valueKind = '';
  @Input() source = '';
  @Input() quality = '';
  @Input() homologation = '';
  @Input() chartType: 'line' | 'bar' = 'bar';
  @Input() seriesName = 'Série';

  rows: { x: string; y: number }[] = [];
  options: EChartsOption = {};

  @Input() set series(value: ChartSeriesInput | null) {
    const points = value?.points || [];
    this.seriesName = value?.name || this.seriesName;
    this.rows = points;
    this.options = {
      color: ['#0e7490', '#163d63', '#c7962d'],
      tooltip: { trigger: 'axis' },
      legend: { show: true, bottom: 0 },
      grid: { left: 48, right: 16, top: 24, bottom: 64 },
      xAxis: {
        type: 'category',
        data: points.map((point) => point.x),
        axisLabel: { color: '#172033', rotate: points.length > 6 ? 35 : 0 },
      },
      yAxis: {
        type: 'value',
        scale: false,
        axisLabel: { color: '#172033' },
        splitLine: { lineStyle: { color: '#dde3ec' } },
      },
      series: [
        {
          name: this.seriesName,
          type: this.chartType === 'line' ? 'line' : 'bar',
          data: points.map((point) => point.y),
          barMaxWidth: 36,
        },
      ],
    };
  }
}
