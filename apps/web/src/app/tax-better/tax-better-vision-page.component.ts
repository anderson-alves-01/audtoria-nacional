import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BiChartInput, BiSeries } from '../shared/bi/bi-chart-options';
import { BiChartComponent, ChartPick } from '../shared/bi/bi-chart.component';
import { SavedView, SavedViews, compareSeries } from '../shared/bi/bi-extras';
import { BiFilters, DimensionValues, syncFiltersWithUrl } from '../shared/bi/bi-filters';
import { DataTableComponent } from '../shared/bi/data-table.component';
import { BiColumn, Cell } from '../shared/bi/table-logic';
import { EmptyStateComponent } from '../shared/states/empty-state.component';
import { BadgeComponent } from '../shared/ui/badge.component';
import { FilterBarComponent } from '../shared/ui/filter-bar.component';
import { KpiCardComponent } from '../shared/ui/kpi-card.component';
import { PanelComponent } from '../shared/ui/panel.component';

interface VisionSide {
  valor: string | null;
  baseCalculo: string | null;
  imposto: string | null;
}

interface VisionRow {
  orgao?: string;
  imposto: string;
  fgo: string;
  periodo?: string | null;
  variables: Record<string, string>;
  operacao: VisionSide;
  malha: VisionSide;
  approved: boolean;
}

interface VisionView {
  createsTaxCredit: boolean;
  approvedExport: boolean;
  emptyReason: string | null;
  rows: VisionRow[];
}

type DimKey = 'imposto' | 'fgo' | 'orgao' | 'periodo';

const UNKNOWN = 'Não informado';
const LABELS: Record<string, string> = {
  imposto: 'Imposto',
  fgo: 'Fato gerador',
  orgao: 'Órgão',
  periodo: 'Período',
};

function num(raw: string | null | undefined): number | null {
  if (raw === null || raw === undefined || raw === '') {
    return null;
  }
  const value = Number(raw);
  return Number.isNaN(value) ? null : value;
}

function dims(row: VisionRow): Record<DimKey, string> {
  return {
    imposto: row.imposto || UNKNOWN,
    fgo: row.fgo || UNKNOWN,
    orgao: row.orgao || UNKNOWN,
    periodo: row.periodo || UNKNOWN,
  };
}

function measureText(value: Cell): string {
  if (value === null || value === undefined || value === '') {
    return '—';
  }
  return typeof value === 'number'
    ? value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 4 })
    : value;
}

/** Soma só os valores gravados; sem nenhum valor o resultado é nulo, nunca zero. */
function total(rows: VisionRow[], pick: (row: VisionRow) => number | null): number | null {
  let sum = 0;
  let seen = false;
  for (const row of rows) {
    const value = pick(row);
    if (value !== null) {
      sum += value;
      seen = true;
    }
  }
  return seen ? sum : null;
}

@Component({
  selector: 'app-tax-better-vision-page',
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
  ],
  templateUrl: './tax-better-vision-page.component.html',
  styleUrl: './tax-better-page.scss',
})
export class TaxBetterVisionPageComponent implements OnInit {
  private readonly http = inject(HttpClient);

  readonly levels: DimKey[] = ['imposto', 'fgo', 'orgao'];
  readonly filters = new BiFilters(this.levels);
  readonly views = new SavedViews('visao');
  readonly dimensions: DimKey[] = ['imposto', 'fgo', 'orgao', 'periodo'];
  readonly labels = LABELS;

  readonly state = signal<'loading' | 'ok' | 'error'>('loading');
  readonly view = signal<VisionView | null>(null);
  readonly errorMessage = signal('');
  readonly search = signal('');
  readonly compareWith = signal('');
  readonly savedViews = signal<SavedView[]>(this.views.list());
  viewName = '';

  constructor() {
    syncFiltersWithUrl(this.filters);
  }

  readonly allRows = computed(() => this.view()?.rows ?? []);

  /** Linhas depois de todos os filtros (selecoes, detalhamento e busca de variavel). */
  readonly rows = computed(() => this.within());

  readonly approvedCount = computed(() => this.rows().filter((row) => row.approved).length);
  readonly sumOperation = computed(() => total(this.rows(), (row) => num(row.operacao.valor)));
  readonly sumMalha = computed(() => total(this.rows(), (row) => num(row.malha.valor)));

  readonly chips = computed(() => this.filters.chips(LABELS));

  readonly mainDimension = computed<DimKey>(() => (this.filters.currentLevel as DimKey | null) ?? 'orgao');

  readonly mainChart = computed<BiChartInput>(() => {
    const dim = this.mainDimension();
    return this.cartesian(dim, 'bar', true);
  });

  readonly fgoChart = computed<BiChartInput>(() => this.cartesian('fgo', 'barH', false));

  readonly periodChart = computed<BiChartInput>(() => this.cartesian('periodo', 'area', true));

  readonly orgaoTreemap = computed<BiChartInput>(() => {
    const rows = this.within('orgao');
    const sums = this.aggregate(rows, 'orgao', (row) => num(row.operacao.valor));
    return {
      kind: 'treemap',
      unit: 'BRL',
      items: [...sums.entries()].map(([name, value]) => ({ name, value })),
    };
  });

  readonly heatmap = computed<BiChartInput>(() => {
    const rows = this.rows();
    const periods = [...new Set(rows.map((row) => dims(row).periodo))].sort();
    const taxes = [...new Set(rows.map((row) => dims(row).imposto))].sort();
    const cells: [number, number, number | null][] = [];
    taxes.forEach((tax, y) => {
      periods.forEach((period, x) => {
        const slice = rows.filter((row) => dims(row).imposto === tax && dims(row).periodo === period);
        cells.push([x, y, total(slice, (row) => num(row.operacao.valor))]);
      });
    });
    return { kind: 'heatmap', unit: 'BRL', categories: periods, rowLabels: taxes, cells };
  });

  readonly periods = computed(() => this.options('periodo'));

  readonly comparison = computed(() => {
    const other = this.compareWith();
    const current = this.filters.selections()['periodo'] ?? [];
    if (!other || current.length !== 1 || current[0] === other) {
      return null;
    }
    const base = this.within('periodo');
    const now = this.aggregate(
      base.filter((row) => dims(row).periodo === current[0]),
      'imposto',
      (row) => num(row.operacao.valor),
    );
    const before = this.aggregate(
      base.filter((row) => dims(row).periodo === other),
      'imposto',
      (row) => num(row.operacao.valor),
    );
    const categories = [...new Set([...now.keys(), ...before.keys()])].sort();
    return { current: current[0], previous: other, rows: compareSeries(categories, now, before) };
  });

  readonly columns: BiColumn<VisionRow>[] = [
    { id: 'orgao', label: 'Órgão', value: (row) => row.orgao || null, width: 120 },
    { id: 'imposto', label: 'Imposto', value: (row) => row.imposto, width: 100 },
    { id: 'fgo', label: 'Fato gerador', value: (row) => row.fgo, width: 160 },
    { id: 'periodo', label: 'Período', value: (row) => row.periodo || null, width: 110 },
    { id: 'variaveis', label: 'Variáveis', value: (row) => this.variables(row), width: 240 },
    { id: 'op_valor', label: 'Operação · valor', value: (row) => num(row.operacao.valor), numeric: true, format: measureText, width: 150 },
    { id: 'op_base', label: 'Operação · base', value: (row) => num(row.operacao.baseCalculo), numeric: true, format: measureText, width: 150 },
    { id: 'op_imposto', label: 'Operação · imposto', value: (row) => num(row.operacao.imposto), numeric: true, format: measureText, width: 160 },
    { id: 'ml_valor', label: 'Malha · valor', value: (row) => num(row.malha.valor), numeric: true, format: measureText, width: 140 },
    { id: 'ml_base', label: 'Malha · base', value: (row) => num(row.malha.baseCalculo), numeric: true, format: measureText, width: 140 },
    { id: 'ml_imposto', label: 'Malha · imposto', value: (row) => num(row.malha.imposto), numeric: true, format: measureText, width: 150 },
    { id: 'aprovacao', label: 'Aprovação', value: (row) => (row.approved ? 'aprovada' : 'sem aprovação'), width: 130 },
  ];

  rowKey = (row: VisionRow): string =>
    [row.orgao, row.imposto, row.fgo, row.periodo, this.variables(row)].join('|');

  ngOnInit(): void {
    this.http.get<VisionView>('/v1/tax-better/vision').subscribe({
      next: (body) => {
        this.view.set({
          createsTaxCredit: false,
          approvedExport: false,
          emptyReason: body.emptyReason,
          rows: body.rows || [],
        });
        this.state.set('ok');
      },
      error: () => {
        this.errorMessage.set('A visão não pôde ser lida.');
        this.state.set('error');
      },
    });
  }

  options(dim: DimKey): string[] {
    const values = new Set<string>();
    for (const row of this.allRows()) {
      const value = dims(row)[dim];
      if (value !== UNKNOWN) {
        values.add(value);
      }
    }
    return [...values].sort((left, right) => left.localeCompare(right, 'pt-BR'));
  }

  selectedOf(dim: DimKey): string {
    return this.filters.selections()[dim]?.[0] ?? '';
  }

  choose(dim: DimKey, value: string): void {
    this.filters.setDimension(dim, value ? [value] : []);
  }

  onPick(pick: ChartPick, dim: DimKey): void {
    this.filters.toggle(dim, pick.value, pick.multi);
  }

  onBrush(values: string[], dim: DimKey): void {
    if (values.length > 0) {
      this.filters.setDimension(dim, values);
    }
  }

  drill(value: string): void {
    this.filters.drillInto(value);
  }

  saveView(): void {
    this.savedViews.set(this.views.save(this.viewName, this.filters.toParams()));
    this.viewName = '';
  }

  applyView(name: string): void {
    const view = this.savedViews().find((entry) => entry.name === name);
    if (view) {
      this.filters.load((key) => view.params[key] ?? null, Object.keys(view.params));
    }
  }

  removeView(name: string): void {
    this.savedViews.set(this.views.remove(name));
  }

  measure(value: number | null): string {
    return measureText(value);
  }

  variables(row: VisionRow): string {
    const pairs = Object.entries(row.variables || {});
    return pairs.length === 0 ? '—' : pairs.map(([key, value]) => `${key}: ${value}`).join('; ');
  }

  variableEntries(row: VisionRow): { key: string; value: string }[] {
    return Object.entries(row.variables || {}).map(([key, value]) => ({ key, value }));
  }

  /** Linhas que passam por todos os filtros, menos o da dimensao informada (selecao cruzada). */
  private within(skip?: string): VisionRow[] {
    const term = this.search().trim().toLowerCase();
    return this.allRows().filter((row) => {
      if (!this.filters.matches(dims(row) as DimensionValues, skip)) {
        return false;
      }
      return !term || this.variables(row).toLowerCase().includes(term);
    });
  }

  private aggregate(
    rows: VisionRow[],
    dim: DimKey,
    pick: (row: VisionRow) => number | null,
  ): Map<string, number | null> {
    const groups = new Map<string, VisionRow[]>();
    for (const row of rows) {
      const key = dims(row)[dim];
      groups.set(key, [...(groups.get(key) ?? []), row]);
    }
    const out = new Map<string, number | null>();
    for (const key of [...groups.keys()].sort((a, b) => a.localeCompare(b, 'pt-BR'))) {
      out.set(key, total(groups.get(key) ?? [], pick));
    }
    return out;
  }

  private cartesian(dim: DimKey, kind: 'bar' | 'barH' | 'area', both: boolean): BiChartInput {
    const rows = this.within(dim);
    const operation = this.aggregate(rows, dim, (row) => num(row.operacao.valor));
    const categories = [...operation.keys()];
    const series: BiSeries[] = [{ name: 'Operação', values: categories.map((key) => operation.get(key) ?? null) }];
    if (both) {
      const malha = this.aggregate(rows, dim, (row) => num(row.malha.valor));
      series.push({ name: 'Malha', values: categories.map((key) => malha.get(key) ?? null) });
    }
    return { kind, unit: 'BRL', categories, series, selected: this.filters.selections()[dim] ?? [] };
  }
}
