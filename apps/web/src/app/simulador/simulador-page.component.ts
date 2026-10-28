import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { HEX_LAYOUT } from '../atlas/hex-layout';
import { BiChartInput } from '../shared/bi/bi-chart-options';
import { BiChartComponent } from '../shared/bi/bi-chart.component';
import { EmptyStateComponent } from '../shared/states/empty-state.component';
import { BadgeComponent } from '../shared/ui/badge.component';
import { KpiCardComponent } from '../shared/ui/kpi-card.component';
import { PanelComponent } from '../shared/ui/panel.component';
import { compactPublishedValue, formatPublishedValue } from '../shared/presentation/official-labels';
import { DEFAULT_OPERATION, EMPTY, SPED_RELIABILITY, SpedSerieItem, SpedView } from '../sped-operacoes/sped-logic';
import {
  GOODS_TYPES,
  RATE_CAVEAT,
  RATE_SOURCE,
  RateVersion,
  ResolvedRate,
  SPED_OPERATIONS,
  SPED_YEARS,
  TAXES,
  TaxId,
  fallbackVersions,
  rateStatusLabel,
  resolveRate,
} from './simulador-aliquotas';
import {
  Comparison,
  PublicYear,
  allowedParam,
  publicByYear,
  referenceFallbackYear,
  referenceYear,
  sanitize,
  scenarioComparison,
  simulatorChart,
  taxAmount,
} from './simulador-logic';

const FALLBACK_BANNER =
  'Simulação aritmética sobre dados públicos exploratórios. Não é apuração fiscal, lançamento, crédito tributário nem decisão.';

const FALLBACK_UFS = HEX_LAYOUT.map((cell) => cell.uf).sort((a, b) => a.localeCompare(b, 'pt-BR'));

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
  private readonly route = inject(ActivatedRoute);

  readonly taxes = TAXES;
  readonly goodsTypes = GOODS_TYPES;
  readonly rateSource = RATE_SOURCE;
  readonly rateCaveat = RATE_CAVEAT;
  readonly reliability = SPED_RELIABILITY;

  readonly state = signal<'loading' | 'ok' | 'error'>('loading');
  readonly view = signal<SpedView<SpedSerieItem> | null>(null);

  /** Versoes de aliquota lidas de /v1/tax-rates. Nulo enquanto carrega ou se a leitura falhar. */
  readonly rateVersions = signal<RateVersion[] | null>(null);
  /** Verdadeiro so quando a leitura terminou com erro (nao enquanto carrega). */
  readonly ratesFallback = signal(false);
  readonly book = computed<RateVersion[]>(() => this.rateVersions() ?? fallbackVersions());

  // Escolhas
  readonly uf = signal<string>('');
  readonly operation = signal<string>(DEFAULT_OPERATION);
  readonly goods = signal<string>('');
  readonly selectedTaxes = signal<TaxId[]>(['ITCD', 'ITBI', 'ISS', 'ICMS']);

  // Cenario desejado (Parte B)
  readonly quantityInput = signal<number | null>(null);
  readonly valueInput = signal<number | null>(null);
  readonly referenceYearInput = signal<number | null>(null);

  /** O simulador funciona sem dado publico: so a comparacao fica em branco. */
  readonly hasPublic = computed(() => this.view()?.run != null);
  readonly items = computed(() => this.view()?.items ?? []);
  readonly years = computed<number[]>(() => this.view()?.years ?? [...SPED_YEARS]);
  readonly operations = computed<string[]>(() => this.view()?.operations ?? [...SPED_OPERATIONS]);
  readonly ufs = computed<string[]>(() => this.view()?.ufs ?? FALLBACK_UFS);
  readonly banner = computed(() => this.view()?.banner || FALLBACK_BANNER);
  readonly ufOrNull = computed(() => this.uf() || null);
  readonly territory = computed(() => this.uf() || 'Brasil, soma das UFs');

  readonly rows = computed<PublicYear[]>(() =>
    publicByYear(this.items(), this.years(), this.operation(), this.ufOrNull()),
  );

  readonly latest = computed<PublicYear | null>(() => this.rows()[this.rows().length - 1] ?? null);

  /** Ano da aliquota do cenario: o ano de comparacao, ou o ultimo ano conhecido. */
  readonly scenarioYear = computed(
    () => this.reference()?.year ?? this.referenceYearInput() ?? this.latest()?.year ?? referenceFallbackYear,
  );

  readonly taxRows = computed(() =>
    this.selectedTaxes().map((tax) => {
      const resolved = this.resolved(tax, this.latest()?.year ?? referenceFallbackYear);
      return { tax, resolved, rate: resolved.rate, amount: taxAmount(this.latest()?.value ?? null, resolved.rate) };
    }),
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

  readonly reference = computed(() =>
    referenceYear(this.rows(), this.referenceYearInput() ?? this.latest()?.year ?? null),
  );

  readonly comparison = computed<Comparison[]>(() =>
    scenarioComparison(this.reference(), this.scenario(), this.selectedTaxes(), this.ufOrNull(), this.book()),
  );

  /** Imposto do cenario informado, um por imposto escolhido. Nunca ha total entre impostos. */
  readonly simulatedTaxes = computed(() =>
    this.selectedTaxes().map((tax) => {
      const resolved = this.resolved(tax, this.scenarioYear());
      return {
        tax,
        resolved,
        rate: resolved.rate,
        simulated: taxAmount(this.scenario().value, resolved.rate),
        published: taxAmount(this.reference()?.value ?? null, resolved.rate),
      };
    }),
  );

  readonly chart = computed<BiChartInput>(() =>
    simulatorChart(
      this.rows(),
      this.selectedTaxes(),
      this.ufOrNull(),
      this.hasScenario() ? this.scenario() : null,
      this.book(),
      this.scenarioYear(),
    ),
  );

  /** Parte A: so dados publicos, sem o ponto simulado. */
  readonly publicChart = computed<BiChartInput>(() =>
    simulatorChart(this.rows(), this.selectedTaxes(), this.ufOrNull(), null, this.book()),
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
    this.http.get<{ items: RateVersion[] }>('/v1/tax-rates').subscribe({
      next: (body) => this.rateVersions.set(body.items ?? []),
      error: () => {
        this.rateVersions.set(null);
        this.ratesFallback.set(true);
      },
    });
    // As listas de UF e operacao do contrato ja valem antes da leitura terminar.
    this.applyQuery();
  }

  /** Abre ja na UF e na operacao vindas do painel SPED, desde que existam nas listas. */
  private applyQuery(): void {
    const query = this.route.snapshot?.queryParamMap;
    if (!query) {
      return;
    }
    this.uf.set(allowedParam(query.get('uf'), this.ufs(), ''));
    this.operation.set(allowedParam(query.get('operacao'), this.operations(), DEFAULT_OPERATION));
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

  /** Aliquota vigente no ano para o imposto e a UF escolhidos. */
  resolved(tax: TaxId, year: number): ResolvedRate {
    return resolveRate(this.book(), tax, this.ufOrNull(), year);
  }

  amountOf(row: PublicYear, tax: TaxId): number | null {
    return taxAmount(row.value, this.resolved(tax, row.year).rate);
  }

  /** Percentual da aliquota, ou o motivo de nao haver um. */
  rateText(resolved: ResolvedRate): string {
    if (resolved.changedWithinYear) {
      return 'muda no ano';
    }
    return resolved.rate === null ? 'sem alíquota' : `${resolved.rate.toLocaleString('pt-BR')}%`;
  }

  /** Percentual mais a situacao jurídica da aliquota. */
  rateMeta(resolved: ResolvedRate, year: number | null): string {
    if (resolved.changedWithinYear) {
      return `A alíquota validada mudou em ${year ?? 'no ano'}; o dado é anual e não pode ser dividido. Imposto em branco.`;
    }
    const status = rateStatusLabel(resolved.status);
    return resolved.rate === null ? 'Sem alíquota para esta escolha' : `Alíquota ${this.rateText(resolved)} · ${status}`;
  }

  statusTone(resolved: ResolvedRate): 'ok' | 'warn' {
    return resolved.status === 'VALIDADO' ? 'ok' : 'warn';
  }
}
