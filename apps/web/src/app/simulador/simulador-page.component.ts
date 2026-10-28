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
import {
  HOMOLOGATION_NEEDS,
  LEVEL_LABEL,
  PublicGate,
  ReliabilityBlock,
  ReliabilityLevel,
  publicDataGate,
} from '../shared/reliability/indicator-reliability';
import { DEFAULT_OPERATION, EMPTY, SpedSerieItem, SpedView } from '../sped-operacoes/sped-logic';
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
  HYPOTHESIS_LABEL,
  PublicYear,
  TRANSFER_DIRECTION_LABEL,
  TRANSFER_DIRECTION_NOTE,
  TRANSFER_ICMS_NOTE,
  TRANSFER_OPERATION,
  TransferDirection,
  allowedParam,
  effectiveTaxes,
  filterByDirection,
  hypothesisChart,
  icmsBlockedForTransfer,
  publicByYear,
  referenceFallbackYear,
  referenceYear,
  sanitize,
  scenarioComparison,
  simulatorChart,
  taxAmount,
} from './simulador-logic';

const FALLBACK_BANNER =
  'Simulação aritmética sobre valores informados por você, tratados como hipótese. Não é apuração fiscal, lançamento, crédito tributário nem decisão.';

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
  readonly hypothesisLabel = HYPOTHESIS_LABEL;
  readonly homologationNeeds = HOMOLOGATION_NEEDS;

  readonly state = signal<'loading' | 'ok' | 'error'>('loading');
  readonly view = signal<SpedView<SpedSerieItem> | null>(null);

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
  readonly operation = signal<string>(DEFAULT_OPERATION);
  readonly goods = signal<string>('');
  readonly selectedTaxes = signal<TaxId[]>(['ITCD', 'ITBI', 'ISS', 'ICMS']);

  // Transferencias: direcao propria e ICMS so por opt-in (hipotese).
  readonly transferDirection = signal<TransferDirection>('');
  readonly icmsTransferOptIn = signal(false);
  readonly directionLabel = TRANSFER_DIRECTION_LABEL;
  readonly directionNote = TRANSFER_DIRECTION_NOTE;
  readonly transferIcmsNote = TRANSFER_ICMS_NOTE;
  readonly isTransfer = computed(() => this.operation() === TRANSFER_OPERATION);
  /** ICMS em branco numa transferencia sem opt-in. */
  readonly icmsBlocked = computed(() => icmsBlockedForTransfer(this.operation(), this.icmsTransferOptIn()));
  /** Impostos que entram em calculo e grafico. */
  readonly activeTaxes = computed(() => effectiveTaxes(this.selectedTaxes(), this.operation(), this.icmsTransferOptIn()));

  // Cenario desejado (Parte B)
  readonly quantityInput = signal<number | null>(null);
  readonly valueInput = signal<number | null>(null);
  readonly referenceYearInput = signal<number | null>(null);

  /** O simulador funciona sem dado publico: com o portao fechado, so a hipotese informada existe. */
  readonly hasPublic = computed(() => this.publicOpen() && this.view()?.run != null);
  /** Nenhum item publico chega aos calculos enquanto o portao estiver fechado. */
  readonly items = computed(() =>
    this.publicOpen() ? filterByDirection(this.view()?.items ?? [], this.operation(), this.transferDirection()) : [],
  );
  readonly years = computed<number[]>(() => this.view()?.years ?? [...SPED_YEARS]);
  readonly operations = computed<string[]>(() => this.view()?.operations ?? [...SPED_OPERATIONS]);
  readonly ufs = computed<string[]>(() => this.view()?.ufs ?? FALLBACK_UFS);
  readonly banner = computed(() => (this.publicOpen() && this.view()?.banner) || FALLBACK_BANNER);
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
    scenarioComparison(this.reference(), this.scenario(), this.activeTaxes(), this.ufOrNull(), this.book()),
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
        )
      : hypothesisChart(this.scenario(), this.activeTaxes(), this.ufOrNull(), this.book(), this.scenarioYear()),
  );

  /** Parte A: so dados publicos, sem o ponto simulado. */
  readonly publicChart = computed<BiChartInput>(() =>
    simulatorChart(this.rows(), this.activeTaxes(), this.ufOrNull(), null, this.book()),
  );

  readonly icmsNeedsUf = computed(() => this.selectedTaxes().includes('ICMS') && !this.uf());

  ngOnInit(): void {
    // Primeiro so a confiabilidade (uma linha). Os dados publicos so sao lidos se o portao abrir.
    const probe = new HttpParams().set('level', 'SERIE').set('pageSize', 1);
    this.http.get<SpedView<SpedSerieItem>>('/v1/sped-operacoes', { params: probe }).subscribe({
      next: (body) => {
        this.reliabilityBlock.set(body.reliability ?? null);
        // Sem itens: as listas de UF, operacao e ano servem aos campos, mas nenhum dado publico entra.
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
    // As listas de UF e operacao do contrato ja valem antes da leitura terminar.
    this.applyQuery();
  }

  /** So roda com o portao aberto, isto e, com todos os indicadores CONFERIDO. */
  private loadPublicData(): void {
    const params = new HttpParams().set('level', 'SERIE').set('pageSize', 1000);
    this.http.get<SpedView<SpedSerieItem>>('/v1/sped-operacoes', { params }).subscribe({
      next: (body) => this.view.set(body),
      error: () => this.state.set('error'),
    });
  }

  levelLabel(level: ReliabilityLevel): string {
    return LEVEL_LABEL[level];
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
    return this.isBlocked(tax) ? null : taxAmount(row.value, this.resolved(tax, row.year).rate);
  }

  /** ICMS de uma transferencia sem opt-in: nao incide por padrao, fica em branco. */
  isBlocked(tax: TaxId): boolean {
    return tax === 'ICMS' && this.icmsBlocked();
  }

  /** Troca a operacao e zera as escolhas que so valem para transferencia. */
  setOperation(value: string): void {
    this.operation.set(value);
    this.transferDirection.set('');
    this.icmsTransferOptIn.set(false);
  }

  /** Meta de um imposto: o motivo do branco numa transferencia, ou a aliquota e sua situacao. */
  taxMeta(tax: TaxId, resolved: ResolvedRate, year: number | null): string {
    return this.isBlocked(tax) ? this.transferIcmsNote : this.rateMeta(resolved, year);
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
    if (resolved.rate === null) {
      return 'Sem alíquota para esta escolha';
    }
    const status = resolved.isSimulation
      ? 'Parâmetro de simulação, não é alíquota da UF nem do município'
      : rateStatusLabel(resolved.status);
    return `Alíquota ${this.rateText(resolved)} · ${status}`;
  }

  statusTone(resolved: ResolvedRate): 'ok' | 'warn' {
    return resolved.status === 'VALIDADO' ? 'ok' : 'warn';
  }
}
