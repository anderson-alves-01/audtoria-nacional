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
import { compactPublishedValue, formatPublishedValue, kpiPublishedValue } from '../shared/presentation/official-labels';
import { PublicGate, ReliabilityBlock, publicDataGate } from '../shared/reliability/indicator-reliability';
import { DEFAULT_OPERATION, EMPTY } from '../sped-operacoes/sped-logic';
import {
  MUNICIPALITY_CATALOG_URL,
  MunicipalityCatalog,
  MunicipalityEntry,
  municipalitiesOf,
  municipalityBelongsTo,
  municipalityName,
} from './simulador-municipios';
import {
  GOODS_TYPES,
  RateVersion,
  ResolvedRate,
  SPED_OPERATIONS,
  SPED_YEARS,
  TAXES,
  TaxId,
  fallbackVersions,
  resolveRate,
} from './simulador-aliquotas';
import {
  CguNfeItem,
  CguNfeView,
  Comparison,
  HYPOTHESIS_LABEL,
  PublicYear,
  ScenarioDriver,
  allowedParam,
  completeFromAverage,
  hypothesisChart,
  publicByYearFromCgu,
  referenceFallbackYear,
  referenceYear,
  sanitize,
  scenarioComparison,
  simulatorChart,
  taxAmount,
  unitValue,
} from './simulador-logic';

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
  readonly operations = SPED_OPERATIONS;
  readonly goodsTypes = GOODS_TYPES;
  readonly hypothesisLabel = HYPOTHESIS_LABEL;

  readonly state = signal<'loading' | 'ok' | 'error'>('loading');
  readonly view = signal<CguNfeView | null>(null);

  /** Confiabilidade dos indicadores lida da API. Nula enquanto carrega ou se a leitura falhar. */
  readonly reliabilityBlock = signal<ReliabilityBlock | null>(null);
  /** Portao dos dados publicos: fechado ate todos os indicadores estarem CONFERIDO (falha fechada). */
  readonly gate = computed<PublicGate>(() => publicDataGate(this.reliabilityBlock()));
  readonly publicOpen = computed(() => this.gate().open);
  /** A comparacao com dado publico so existe com o portao aberto e uma carga validada. */
  readonly comparisonEnabled = computed(() => this.publicOpen() && this.view()?.run != null);

  /** Versoes de aliquota lidas de /v1/tax-rates. Nulo enquanto carrega ou se a leitura falhar. */
  readonly rateVersions = signal<RateVersion[] | null>(null);
  /** Verdadeiro so quando a leitura terminou com erro (nao enquanto carrega). */
  readonly ratesFallback = signal(false);
  readonly book = computed<RateVersion[]>(() => this.rateVersions() ?? fallbackVersions());

  // Escolhas
  readonly uf = signal<string>('');
  /** Municipio (codigo IBGE de 7 digitos). Depende da UF: zera ao trocar de UF. */
  readonly municipality = signal<string>('');
  /** Lista de municipios do IBGE, lida uma vez do arquivo versionado quando a primeira UF e escolhida. */
  readonly municipalityCatalog = signal<MunicipalityEntry[] | null>(null);
  readonly municipalityState = signal<'idle' | 'loading' | 'ok' | 'error'>('idle');
  readonly municipalityOptions = computed(() => municipalitiesOf(this.municipalityCatalog(), this.ufOrNull()));
  /** So vale um municipio da lista que pertence a UF escolhida. */
  readonly municipalityOrNull = computed(() => {
    const code = this.municipality();
    return municipalityBelongsTo(this.municipalityCatalog(), this.ufOrNull(), code) ? code : null;
  });
  readonly municipalityLabel = computed(() => municipalityName(this.municipalityCatalog(), this.municipalityOrNull()));
  readonly goods = signal<string>('');
  readonly operation = signal<string>(DEFAULT_OPERATION);
  readonly selectedTaxes = signal<TaxId[]>(['ITCD', 'ITBI', 'ISS', 'ICMS']);
  readonly sourceLabel = 'NF-e CGU · UF do emitente';
  /** Impostos que entram em calculo e grafico. */
  readonly activeTaxes = computed(() => this.selectedTaxes());

  // Cenario desejado (Parte B)
  readonly quantityInput = signal<number | null>(null);
  readonly valueInput = signal<number | null>(null);
  readonly driver = signal<ScenarioDriver>(null);
  readonly referenceYearInput = signal<number | null>(null);

  /** O simulador funciona sem dado publico: com o portao fechado, so a hipotese informada existe. */
  readonly hasPublic = computed(() => this.publicOpen() && this.view()?.run != null);
  /** Nenhum item publico chega aos calculos enquanto o portao estiver fechado. */
  readonly items = computed<CguNfeItem[]>(() => (this.publicOpen() ? (this.view()?.items ?? []) : []));
  readonly years = computed<number[]>(() => this.view()?.years ?? [...SPED_YEARS]);
  readonly ufs = computed<string[]>(() => this.view()?.ufs ?? FALLBACK_UFS);
  readonly coverage = computed(() => this.view()?.coverage ?? 'AUSENTE');
  readonly ufOrNull = computed(() => this.uf() || null);
  readonly territory = computed(() => {
    const place = this.uf() || 'Brasil, soma das UFs';
    return this.operation() ? `${place} · ${this.operation()}` : place;
  });

  readonly rows = computed<PublicYear[]>(() => publicByYearFromCgu(this.items(), this.years(), this.ufOrNull()));

  readonly latest = computed<PublicYear | null>(() => this.rows()[this.rows().length - 1] ?? null);

  /** Ano da aliquota do cenario: o ano de comparacao, ou o ultimo ano conhecido. */
  readonly scenarioYear = computed(
    () => this.reference()?.year ?? this.referenceYearInput() ?? this.latest()?.year ?? referenceFallbackYear,
  );

  readonly taxRows = computed(() =>
    this.selectedTaxes().map((tax) => {
      const resolved = this.resolved(tax, this.latest()?.year ?? referenceFallbackYear);
      const blocked = this.isBlocked(tax);
      return {
        tax,
        resolved,
        rate: resolved.rate,
        blocked,
        amount: blocked ? null : taxAmount(this.latest()?.value ?? null, resolved.rate),
      };
    }),
  );

  readonly average = computed(() =>
    this.hasPublic() ? unitValue(this.reference()?.quantity ?? null, this.reference()?.value ?? null) : null,
  );

  readonly scenario = computed(() =>
    completeFromAverage(
      sanitize(this.quantityInput()),
      sanitize(this.valueInput()),
      this.average(),
      this.driver(),
    ),
  );

  readonly quantityShown = computed(() =>
    this.driver() === 'value' ? this.scenario().quantity : this.quantityInput(),
  );
  readonly valueShown = computed(() =>
    this.driver() === 'quantity' ? this.scenario().value : this.valueInput(),
  );
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
    scenarioComparison(
      this.reference(),
      this.scenario(),
      this.activeTaxes(),
      this.ufOrNull(),
      this.book(),
      this.municipalityOrNull(),
    ),
  );

  /** Imposto do cenario informado, um por imposto escolhido. Nunca ha total entre impostos. */
  readonly simulatedTaxes = computed(() =>
    this.selectedTaxes().map((tax) => {
      const resolved = this.resolved(tax, this.scenarioYear());
      const blocked = this.isBlocked(tax);
      return {
        tax,
        resolved,
        rate: resolved.rate,
        blocked,
        simulated: blocked ? null : taxAmount(this.scenario().value, resolved.rate),
        published:
          this.comparisonEnabled() && !blocked ? taxAmount(this.reference()?.value ?? null, resolved.rate) : null,
      };
    }),
  );

  /** Com o portao fechado o grafico traz so a hipotese informada, sem nenhum dado publico. */
  readonly chart = computed<BiChartInput>(() =>
    this.publicOpen()
      ? simulatorChart(
          this.rows(),
          this.activeTaxes(),
          this.ufOrNull(),
          this.hasScenario() ? this.scenario() : null,
          this.book(),
          this.scenarioYear(),
          this.municipalityOrNull(),
        )
      : hypothesisChart(
          this.scenario(),
          this.activeTaxes(),
          this.ufOrNull(),
          this.book(),
          this.scenarioYear(),
          this.municipalityOrNull(),
        ),
  );

  /** Parte A: so dados publicos, sem o ponto simulado. */
  readonly publicChart = computed<BiChartInput>(() =>
    simulatorChart(
      this.rows(),
      this.activeTaxes(),
      this.ufOrNull(),
      null,
      this.book(),
      referenceFallbackYear,
      this.municipalityOrNull(),
    ),
  );

  ngOnInit(): void {
    // Primeiro so a confiabilidade (uma linha). Os dados publicos so sao lidos se o portao abrir.
    const probe = new HttpParams().set('pageSize', 1);
    this.http.get<CguNfeView>('/v1/cgu-nfe', { params: probe }).subscribe({
      next: (body) => {
        this.reliabilityBlock.set(body.reliability ?? null);
        // Sem itens: as listas de UF e ano servem aos campos, mas nenhum dado publico entra.
        this.view.set({ ...body, items: [] });
        this.state.set('ok');
        if (this.publicOpen()) {
          this.loadPublicData();
        }
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
    // A lista de UF do contrato ja vale antes da leitura terminar.
    this.applyQuery();
  }

  /** So roda com o portao aberto, isto e, com todos os indicadores CONFERIDO. */
  private loadPublicData(): void {
    const params = new HttpParams().set('pageSize', 1000);
    this.http.get<CguNfeView>('/v1/cgu-nfe', { params }).subscribe({
      next: (body) => this.view.set(body),
      error: () => this.state.set('error'),
    });
  }

  /** Abre ja na UF e na operacao vindas do painel SPED, se existirem na lista. */
  private applyQuery(): void {
    const query = this.route.snapshot?.queryParamMap;
    if (!query) {
      return;
    }
    this.setUf(allowedParam(query.get('uf'), this.ufs(), ''));
    this.operation.set(allowedParam(query.get('operacao'), this.operations, DEFAULT_OPERATION));
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

  setQuantity(raw: unknown): void {
    this.driver.set('quantity');
    this.quantityInput.set(this.parse(raw));
  }

  setValue(raw: unknown): void {
    this.driver.set('value');
    this.valueInput.set(this.parse(raw));
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

  kpiMoney(value: number | null): string {
    return value === null ? EMPTY : kpiPublishedValue(value, 'BRL');
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
    return resolveRate(this.book(), tax, this.ufOrNull(), year, this.municipalityOrNull());
  }

  amountOf(row: PublicYear, tax: TaxId): number | null {
    return this.isBlocked(tax) ? null : taxAmount(row.value, this.resolved(tax, row.year).rate);
  }

  /** Troca a UF: o municipio escolhido deixa de valer e a lista do IBGE e lida na primeira escolha. */
  setUf(value: string): void {
    this.uf.set(value);
    this.municipality.set('');
    if (value) {
      this.loadMunicipalities();
    }
  }

  setMunicipality(value: string): void {
    this.municipality.set(municipalityBelongsTo(this.municipalityCatalog(), this.ufOrNull(), value) ? value : '');
  }

  private loadMunicipalities(): void {
    if (this.municipalityState() !== 'idle') {
      return;
    }
    this.municipalityState.set('loading');
    this.http.get<MunicipalityCatalog>(MUNICIPALITY_CATALOG_URL).subscribe({
      next: (body) => {
        this.municipalityCatalog.set(body.municipios ?? []);
        this.municipalityState.set('ok');
      },
      error: () => {
        this.municipalityCatalog.set(null);
        this.municipalityState.set('error');
      },
    });
  }

  isBlocked(_tax: TaxId): boolean {
    return false;
  }

  taxMeta(_tax: TaxId, resolved: ResolvedRate, year: number | null): string {
    return this.rateMeta(resolved, year);
  }

  /** Percentual da aliquota, ou o motivo de nao haver um. */
  rateText(resolved: ResolvedRate): string {
    if (resolved.changedWithinYear) {
      return 'muda no ano';
    }
    return resolved.rate === null ? 'sem alíquota' : `${resolved.rate.toLocaleString('pt-BR')}%`;
  }

  /** Percentual da aliquota no cartão, sem texto de regra. */
  rateMeta(resolved: ResolvedRate, _year: number | null): string {
    return this.rateText(resolved);
  }

  statusTone(resolved: ResolvedRate): 'ok' | 'warn' {
    return resolved.status === 'VALIDADO' ? 'ok' : 'warn';
  }
}
