import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BiChartInput } from '../shared/bi/bi-chart-options';
import { BiChartComponent } from '../shared/bi/bi-chart.component';
import { EmptyStateComponent } from '../shared/states/empty-state.component';
import { BadgeComponent } from '../shared/ui/badge.component';
import { KpiCardComponent } from '../shared/ui/kpi-card.component';
import { PanelComponent } from '../shared/ui/panel.component';
import { compactPublishedValue, formatPublishedValue } from '../shared/presentation/official-labels';
import { DEFAULT_OPERATION, EMPTY, SpedSerieItem, SpedView } from '../sped-operacoes/sped-logic';
import { GOODS_TYPES, RATE_SOURCE, TAXES, TaxId, rateFor } from './simulador-aliquotas';
import {
  Comparison,
  PublicYear,
  publicByYear,
  referenceYear,
  sanitize,
  scenarioComparison,
  simulatorChart,
  taxAmount,
} from './simulador-logic';

const FALLBACK_BANNER =
  'Simulação aritmética sobre dados públicos exploratórios. Não é apuração fiscal, lançamento, crédito tributário nem decisão. O valor por UF é rateio estimado.';

@Component({
  selector: 'app-simulador-page',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    KpiCardComponent,
    EmptyStateComponent,
    PanelComponent,
    BiChartComponent,
    BadgeComponent,
  ],
  templateUrl: './simulador-page.component.html',
  styleUrl: './simulador-page.component.scss',
})
export class SimuladorPageComponent implements OnInit {
  private readonly http = inject(HttpClient);

  readonly taxes = TAXES;
  readonly goodsTypes = GOODS_TYPES;
  readonly rateSource = RATE_SOURCE;

  readonly state = signal<'loading' | 'ok' | 'error'>('loading');
  readonly view = signal<SpedView<SpedSerieItem> | null>(null);

  // Parte A
  readonly uf = signal<string>('');
  readonly operation = signal<string>(DEFAULT_OPERATION);
  readonly goods = signal<string>('');
  readonly selectedTaxes = signal<TaxId[]>(['ITCD', 'ITBI', 'ISS', 'ICMS']);

  // Parte B
  readonly quantityInput = signal<number | null>(null);
  readonly valueInput = signal<number | null>(null);
  readonly referenceYearInput = signal<number | null>(null);

  readonly items = computed(() => this.view()?.items ?? []);
  readonly years = computed(() => this.view()?.years ?? []);
  readonly operations = computed(() => this.view()?.operations ?? []);
  readonly ufs = computed(() => this.view()?.ufs ?? []);
  readonly banner = computed(() => this.view()?.banner || FALLBACK_BANNER);
  readonly ufOrNull = computed(() => this.uf() || null);
  readonly territory = computed(() => this.uf() || 'Brasil, soma das UFs');

  readonly rows = computed<PublicYear[]>(() =>
    publicByYear(this.items(), this.years(), this.operation(), this.ufOrNull()),
  );

  readonly latest = computed<PublicYear | null>(() => this.rows()[this.rows().length - 1] ?? null);

  readonly taxRows = computed(() =>
    this.selectedTaxes().map((tax) => ({
      tax,
      rate: rateFor(tax, this.ufOrNull()),
      amount: taxAmount(this.latest()?.value ?? null, rateFor(tax, this.ufOrNull())),
    })),
  );

  readonly scenario = computed(() => ({
    quantity: sanitize(this.quantityInput()),
    value: sanitize(this.valueInput()),
  }));
  readonly hasScenario = computed(() => this.scenario().quantity !== null || this.scenario().value !== null);
  readonly inputInvalid = computed(
    () =>
      (this.quantityInput() !== null && this.scenario().quantity === null) ||
      (this.valueInput() !== null && this.scenario().value === null),
  );

  readonly reference = computed(() => referenceYear(this.rows(), this.referenceYearInput() ?? this.latest()?.year ?? null));

  readonly comparison = computed<Comparison[]>(() =>
    scenarioComparison(this.reference(), this.scenario(), this.selectedTaxes(), this.ufOrNull()),
  );

  readonly chart = computed<BiChartInput>(() =>
    simulatorChart(this.rows(), this.selectedTaxes(), this.ufOrNull(), this.hasScenario() ? this.scenario() : null),
  );

  readonly icmsNeedsUf = computed(() => this.selectedTaxes().includes('ICMS') && !this.uf());

  ngOnInit(): void {
    const params = new HttpParams().set('level', 'SERIE').set('pageSize', 1000);
    this.http.get<SpedView<SpedSerieItem>>('/v1/sped-operacoes', { params }).subscribe({
      next: (body) => {
        this.view.set(body);
        this.state.set('ok');
      },
      error: () => this.state.set('error'),
    });
  }

  isTaxSelected(tax: TaxId): boolean {
    return this.selectedTaxes().includes(tax);
  }

  toggleTax(tax: TaxId, checked: boolean): void {
    const current = this.selectedTaxes();
    const next = checked ? [...new Set([...current, tax])] : current.filter((entry) => entry !== tax);
    this.selectedTaxes.set(TAXES.map((def) => def.id).filter((id) => next.includes(id)));
  }

  /** Numero do campo. Texto vazio vira nulo. */
  parse(raw: unknown): number | null {
    return raw === '' || raw === null || raw === undefined ? null : Number(raw);
  }

  money(value: number | null): string {
    return value === null ? EMPTY : formatPublishedValue(value, 'BRL');
  }

  count(value: number | null): string {
    return value === null ? EMPTY : formatPublishedValue(value, 'COUNT');
  }

  compact(value: number | null, unit: 'BRL' | 'COUNT'): string {
    return value === null ? EMPTY : compactPublishedValue(value, unit);
  }

  cell(value: number | null, unit: 'BRL' | 'COUNT'): string {
    return unit === 'BRL' ? this.money(value) : this.count(value);
  }

  percent(value: number | null): string {
    return value === null
      ? EMPTY
      : `${value.toLocaleString('pt-BR', { maximumFractionDigits: 1, minimumFractionDigits: 1 })}%`;
  }

  rateForUf(tax: TaxId): number | null {
    return rateFor(tax, this.ufOrNull());
  }

  amountOf(row: PublicYear, tax: TaxId): number | null {
    return taxAmount(row.value, rateFor(tax, this.ufOrNull()));
  }

  rateText(rate: number | null): string {
    return rate === null ? 'pendente' : `${rate.toLocaleString('pt-BR')}%`;
  }
}
