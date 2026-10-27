import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Component, OnInit, computed, effect, inject, signal, untracked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BiChartInput } from '../shared/bi/bi-chart-options';
import { compactPublishedValue } from '../shared/presentation/official-labels';
import { BiChartComponent, ChartPick } from '../shared/bi/bi-chart.component';
import { BiFilters, syncFiltersWithUrl } from '../shared/bi/bi-filters';
import { DataTableComponent } from '../shared/bi/data-table.component';
import { BiColumn, Cell } from '../shared/bi/table-logic';
import { EmptyStateComponent } from '../shared/states/empty-state.component';
import { BadgeComponent } from '../shared/ui/badge.component';
import { FilterBarComponent } from '../shared/ui/filter-bar.component';
import { KpiCardComponent } from '../shared/ui/kpi-card.component';
import { PanelComponent } from '../shared/ui/panel.component';
import { SpedHexMapComponent } from './sped-hex-map.component';
import {
  DEFAULT_OPERATION,
  EMPTY,
  SpedCfopItem,
  SpedSerieItem,
  SpedView,
  byOperation,
  byUf,
  byYear,
  formatMeasure,
  money,
  pick,
  sumKnown,
} from './sped-logic';

const LABELS: Record<string, string> = { ano: 'Ano', uf: 'UF', operacao: 'Operação' };
const TABLE_PAGE_SIZE = 500;
const FALLBACK_BANNER =
  'Base exploratória, não homologada. O valor por UF é rateio estimado de totais nacionais, não valor fiscal efetivo. Não é crédito tributário.';

function brl(value: Cell): string {
  return typeof value === 'number' ? formatMeasure(value, 'valor') : EMPTY;
}

@Component({
  selector: 'app-sped-operacoes-page',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    KpiCardComponent,
    EmptyStateComponent,
    PanelComponent,
    BiChartComponent,
    DataTableComponent,
    FilterBarComponent,
    BadgeComponent,
    SpedHexMapComponent,
  ],
  templateUrl: './sped-operacoes-page.component.html',
  styleUrl: './sped-operacoes-page.component.scss',
})
export class SpedOperacoesPageComponent implements OnInit {
  private readonly http = inject(HttpClient);

  readonly filters = new BiFilters([]);
  readonly labels = LABELS;
  readonly state = signal<'loading' | 'ok' | 'error'>('loading');
  readonly view = signal<SpedView<SpedSerieItem> | null>(null);
  readonly errorMessage = signal('');

  readonly cfopView = signal<SpedView<SpedCfopItem> | null>(null);
  readonly cfopState = signal<'idle' | 'loading' | 'ok' | 'error'>('idle');
  readonly page = signal(1);
  private cfopRequest = 0;
  private lastTableKey = '';

  constructor() {
    syncFiltersWithUrl(this.filters);
    effect(() => {
      const key = this.tableKey();
      const page = this.page();
      const ready = this.view()?.run != null;
      untracked(() => {
        if (!ready) {
          return;
        }
        if (key !== this.lastTableKey) {
          this.lastTableKey = key;
          if (page !== 1) {
            this.page.set(1);
            return;
          }
        }
        this.loadCfop(page);
      });
    });
  }

  readonly items = computed(() => this.view()?.items ?? []);
  readonly years = computed(() => this.view()?.years ?? [2021, 2022, 2023, 2024, 2025]);
  readonly operations = computed(() => this.view()?.operations ?? []);
  readonly ufs = computed(() => this.view()?.ufs ?? []);
  readonly banner = computed(() => this.view()?.banner || FALLBACK_BANNER);

  readonly ano = computed(() => this.filters.selections()['ano']?.[0] ?? null);
  readonly uf = computed(() => this.filters.selections()['uf']?.[0] ?? null);
  readonly operacao = computed(() => this.filters.selections()['operacao']?.[0] ?? null);
  readonly activeOperation = computed(() => this.operacao() ?? DEFAULT_OPERATION);
  readonly chips = computed(() => this.filters.chips(LABELS));
  readonly tableKey = computed(() => [this.ano(), this.uf(), this.operacao()].join('|'));

  private readonly focused = computed(() =>
    pick(this.items(), { ano: this.ano(), uf: this.uf(), operacao: this.activeOperation() }),
  );
  readonly quantity = computed(() => (this.focused().length === 0 ? null : sumKnown(this.focused().map((row) => row.quantidade))));
  readonly estimated = computed(() =>
    this.focused().length === 0 ? null : sumKnown(this.focused().map((row) => money(row.valorEstimado))),
  );
  readonly ufsWithOccurrence = computed(() => {
    const map = byUf(this.items(), this.activeOperation(), 'quantidade', this.ano());
    return [...map.values()].filter((value) => value !== null && value > 0).length;
  });

  readonly quantityMap = computed(() => byUf(this.items(), this.activeOperation(), 'quantidade', this.ano()));
  readonly valueMap = computed(() => byUf(this.items(), this.activeOperation(), 'valor', this.ano()));

  readonly quantityByOperation = computed<BiChartInput>(() =>
    this.operationChart('quantidade', 'COUNT', 'Quantidade'),
  );
  readonly valueByOperation = computed<BiChartInput>(() => this.operationChart('valor', 'BRL', 'Valor estimado'));
  readonly quantityByYear = computed<BiChartInput>(() => this.yearChart('quantidade', 'COUNT', 'Quantidade'));
  readonly valueByYear = computed<BiChartInput>(() => this.yearChart('valor', 'BRL', 'Valor estimado'));

  readonly columns: BiColumn<SpedCfopItem>[] = [
    { id: 'ano', label: 'Ano', value: (row) => String(row.ano), width: 80 },
    { id: 'uf', label: 'UF', value: (row) => row.uf, width: 70 },
    { id: 'operacao', label: 'Operação', value: (row) => row.operacao, width: 210 },
    { id: 'cfop', label: 'CFOP', value: (row) => row.cfop, width: 90 },
    { id: 'quantidade', label: 'Quantidade (observada)', value: (row) => row.quantidade, numeric: true, width: 170 },
    {
      id: 'valor',
      label: 'Valor estimado (R$)',
      value: (row) => money(row.valorEstimado),
      numeric: true,
      format: brl,
      width: 180,
    },
  ];

  rowKey = (row: SpedCfopItem): string => [row.ano, row.uf, row.operacao, row.cfop].join('|');

  readonly pageCount = computed(() => {
    const view = this.cfopView();
    return view ? Math.max(1, Math.ceil(view.total / view.pageSize)) : 1;
  });

  ngOnInit(): void {
    const params = new HttpParams().set('level', 'SERIE').set('pageSize', 1000);
    this.http.get<SpedView<SpedSerieItem>>('/v1/sped-operacoes', { params }).subscribe({
      next: (body) => {
        this.view.set(body);
        this.state.set('ok');
      },
      error: () => {
        this.errorMessage.set('Os dados do SPED não puderam ser lidos.');
        this.state.set('error');
      },
    });
  }

  choose(dim: 'ano' | 'uf' | 'operacao', value: string): void {
    this.filters.setDimension(dim, value ? [value] : []);
  }

  selectedOf(dim: 'ano' | 'uf' | 'operacao'): string {
    return this.filters.selections()[dim]?.[0] ?? '';
  }

  onPick(pickEvent: ChartPick, dim: 'ano' | 'operacao'): void {
    this.filters.toggle(dim, pickEvent.value, false);
  }

  onMap(uf: string): void {
    this.filters.toggle('uf', uf, false);
  }

  format(value: number | null, measure: 'quantidade' | 'valor'): string {
    return formatMeasure(value, measure);
  }

  /** Valor grande em forma curta para o cartão. O valor exato fica na tabela. */
  compact(value: number | null, measure: 'quantidade' | 'valor'): string {
    if (value === null) {
      return EMPTY;
    }
    return compactPublishedValue(value, measure === 'valor' ? 'BRL' : 'COUNT');
  }

  previous(): void {
    this.page.set(Math.max(1, this.page() - 1));
  }

  next(): void {
    this.page.set(Math.min(this.pageCount(), this.page() + 1));
  }

  private loadCfop(page: number): void {
    const request = ++this.cfopRequest;
    let params = new HttpParams().set('level', 'CFOP').set('page', page).set('pageSize', TABLE_PAGE_SIZE);
    for (const [name, value] of [
      ['ano', this.ano()],
      ['uf', this.uf()],
      ['operacao', this.operacao()],
    ] as const) {
      if (value) {
        params = params.set(name, value);
      }
    }
    this.cfopState.set('loading');
    this.http.get<SpedView<SpedCfopItem>>('/v1/sped-operacoes', { params }).subscribe({
      next: (body) => {
        if (request === this.cfopRequest) {
          this.cfopView.set(body);
          this.cfopState.set('ok');
        }
      },
      error: () => {
        if (request === this.cfopRequest) {
          this.cfopState.set('error');
        }
      },
    });
  }

  private operationChart(measure: 'quantidade' | 'valor', unit: string, name: string): BiChartInput {
    const operations = this.operations();
    const values = byOperation(this.items(), operations, measure, { ano: this.ano(), uf: this.uf() });
    return {
      kind: 'barH',
      unit,
      categories: operations,
      series: [{ name, values: operations.map((operation) => values.get(operation) ?? null) }],
      selected: this.operacao() ? [this.operacao() as string] : [],
    };
  }

  private yearChart(measure: 'quantidade' | 'valor', unit: string, name: string): BiChartInput {
    const years = this.years();
    return {
      kind: 'line',
      unit,
      categories: years.map(String),
      series: [
        {
          name: `${name} · ${this.activeOperation()}`,
          values: byYear(this.items(), years, this.activeOperation(), measure, this.uf()),
        },
      ],
      selected: this.ano() ? [this.ano() as string] : [],
    };
  }
}
