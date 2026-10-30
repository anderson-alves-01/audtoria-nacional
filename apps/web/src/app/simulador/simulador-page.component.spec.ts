import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { APP_NAV_GROUPS, OPEN_NAV_GROUP_IDS } from '../layout/navigation';
import { PUBLIC_DATA_INDICATORS, ReliabilityBlock, ReliabilityLevel } from '../shared/reliability/indicator-reliability';
import { RateVersion } from './simulador-aliquotas';
import { SimuladorPageComponent } from './simulador-page.component';

const run = {
  runId: 'synth-cgu',
  layoutVersion: 'cgu-nfe-v1',
  competence: '2021-01..2025-12',
  monthsProcessed: 53,
  loadedAt: '2026-10-29T12:00:00+00:00',
};

function reliability(level: ReliabilityLevel | Partial<Record<string, ReliabilityLevel>>): ReliabilityBlock {
  const levelOf = (id: string): ReliabilityLevel | undefined => (typeof level === 'string' ? level : level[id]);
  return {
    levels: ['NAO_CONFIAVEL', 'EXPLORATORIO', 'CONFERIDO'],
    indicators: PUBLIC_DATA_INDICATORS.filter((id) => levelOf(id) !== undefined).map((id) => {
      const current = levelOf(id) as ReliabilityLevel;
      return {
        id,
        label: `Indicador ${id}`,
        level: current,
        reason: `Motivo de ${id}`,
        evidence: current === 'CONFERIDO' ? ['evidence/ops/exemplo.md'] : [],
        usableForFiscalCalculation: current === 'CONFERIDO',
        publishableInSimulator: current === 'CONFERIDO',
        usableAsHypothesis: current !== 'NAO_CONFIAVEL',
      };
    }),
  };
}

function view(
  items: unknown[],
  options: { withRun?: boolean; years?: number[]; block?: ReliabilityBlock | null } = {},
): Record<string, unknown> {
  const { withRun = true, years = [2021, 2022], block = reliability('NAO_CONFIAVEL') } = options;
  return {
    sourceId: 'CGU-NFE',
    valueKind: 'OBSERVED_DOCUMENT_CENTS',
    banner: 'NF-e da CGU. UF do emitente. Valor de documento não é pagamento.',
    formula: 'itens_exceto_canceladas; valor_itens_exceto_canceladas',
    homologated: false,
    published: false,
    createsTaxCredit: false,
    coverage: 'PARCIAL',
    monthsProcessed: 53,
    monthsMissing: ['202101'],
    ...(block ? { reliability: block } : {}),
    page: 1,
    pageSize: 1000,
    total: items.length,
    years,
    ufs: ['AC', 'SP', 'MG'],
    run: withRun ? run : null,
    items,
  };
}

const flat = (tax: string, rate: number) => ({
  tax, uf: 'BR', rateKind: 'UNICA', rate, validFrom: null, validTo: null,
  legalBasis: null, officialUrl: null, status: 'PENDENTE', note: null,
});
const acre = (rate: number, validFrom: string | null, validTo: string | null) => ({
  tax: 'ICMS', uf: 'AC', rateKind: 'MODAL', rate, validFrom, validTo,
  legalBasis: 'LC/AC 422/2022', officialUrl: null, status: 'VALIDADO', note: null,
});
const RATES = [
  flat('ITCD', 6),
  flat('ITBI', 3),
  flat('ISS', 5),
  { ...flat('ICMS', 18), uf: 'SP', rateKind: 'MODAL' },
  acre(17, null, '2023-03-31'),
  acre(19, '2023-04-01', null),
];

function flushRates(http: HttpTestingController, rates: unknown[] | 'error' = RATES): void {
  const request = http.expectOne('/v1/tax-rates');
  if (rates === 'error') {
    request.flush('x', { status: 500, statusText: 'err' });
  } else {
    request.flush({ items: rates });
  }
}

const ITEMS = [
  { ano: 2021, uf: 'SP', itens: 100, valorItens: '1000.00', notas: 10, valorNotas: '900.00' },
  { ano: 2022, uf: 'SP', itens: 200, valorItens: '2000.00', notas: 20, valorNotas: '1800.00' },
  { ano: 2022, uf: 'MG', itens: 999, valorItens: '9999.00', notas: 1, valorNotas: '1.00' },
];

const isProbe = (req: { url: string; params: { get(name: string): string | null } }) =>
  req.url === '/v1/cgu-nfe' && req.params.get('pageSize') === '1';
const isFullRead = (req: { url: string; params: { get(name: string): string | null } }) =>
  req.url === '/v1/cgu-nfe' && req.params.get('pageSize') === '1000';

describe('SimuladorPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SimuladorPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();
  });

  /** Fonte NAO_CONFIAVEL, como a API devolve hoje. O corpo traz itens para provar que a tela os descarta. */
  function blocked(items: unknown[] = ITEMS, block: ReliabilityBlock | null = reliability('NAO_CONFIAVEL')) {
    const fixture = TestBed.createComponent(SimuladorPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(isProbe).flush(view(items, { block }));
    flushRates(http);
    http.expectNone(isFullRead);
    fixture.detectChanges();
    return { fixture, http, page: fixture.componentInstance, el: fixture.nativeElement as HTMLElement };
  }

  /** Portão aberto: todos os indicadores CONFERIDO. Caminho que só existe depois de uma base homologada. */
  function opened(items: unknown[] = ITEMS, years = [2021, 2022]) {
    const fixture = TestBed.createComponent(SimuladorPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(isProbe).flush(view([], { block: reliability('CONFERIDO'), years }));
    http.expectOne(isFullRead).flush(view(items, { block: reliability('CONFERIDO'), years }));
    flushRates(http);
    fixture.detectChanges();
    return { fixture, http, page: fixture.componentInstance, el: fixture.nativeElement as HTMLElement };
  }

  it('sits above Visão geral in the menu and is open by default', () => {
    const ids = APP_NAV_GROUPS.map((group) => group.id);
    expect(ids.indexOf('simulador')).toBeGreaterThanOrEqual(0);
    expect(ids.indexOf('simulador')).toBe(ids.indexOf('visao') - 1);
    expect(OPEN_NAV_GROUP_IDS).toContain('simulador');
    expect(APP_NAV_GROUPS.find((group) => group.id === 'simulador')?.links[0].path).toBe('/simulador');
  });

  describe('with the public source NAO_CONFIAVEL', () => {
    it('blocks the public data and says why, without rendering any CGU number', () => {
      const { page, el, http } = blocked();
      const text = el.textContent as string;
      expect(page.publicOpen()).toBeFalse();
      expect(el.querySelector('[data-testid="public-blocked"]')).toBeTruthy();
      expect(text).toContain('Fonte pública NAO_CONFIAVEL: indicadores não são usados no Simulador');
      expect(text).not.toContain('O que falta para liberar');
      expect(text).not.toContain('Motivo de cgu_nfe_itens_uf_ano');
      // Os itens vieram no corpo (999 e R$ 9.999,00) e nada disso chega à tela nem aos cálculos.
      expect(page.items()).toEqual([]);
      expect(text).not.toContain('999');
      expect(text).not.toContain('Quantidade, valor e imposto por ano');
      expect(el.querySelector('table')).toBeNull();
      expect(el.querySelectorAll('app-bi-chart').length).toBe(0);
      http.verify();
    });

    it('reads only the reliability row, never the full public data', () => {
      const { http } = blocked();
      http.expectNone(isFullRead);
      http.verify();
    });

    it('keeps the fields usable and labels every result as a manual hypothesis', async () => {
      const { fixture, page, el, http } = blocked();
      page.uf.set('SP');
      fixture.detectChanges();
      await fixture.whenStable();
      expect(el.querySelector('input[name="qtd"]')).toBeTruthy();
      expect(el.querySelector('input[name="valor"]')).toBeTruthy();
      expect(el.querySelector('select[name="operacao"]')).toBeTruthy();
      const value = el.querySelector('input[name="valor"]') as HTMLInputElement;
      value.value = '5000';
      value.dispatchEvent(new Event('input'));
      fixture.detectChanges();
      expect(page.valueInput()).toBe(5000);
      expect(page.simulatedTaxes().find((row) => row.tax === 'ITCD')?.simulated).toBe(300);
      expect(page.simulatedTaxes().find((row) => row.tax === 'ICMS')?.simulated).toBe(900);
      const text = el.textContent as string;
      expect(text).toContain('ITCD do cenário');
      expect(text).toContain('Hipótese informada manualmente');
      expect(el.querySelectorAll('app-kpi-card').length).toBe(4);
      http.verify();
    });

    it('draws only the hypothesis, with no public series', () => {
      const { fixture, page, http } = blocked();
      page.uf.set('SP');
      page.quantityInput.set(300);
      page.valueInput.set(5000);
      fixture.detectChanges();
      const chart = page.chart();
      expect(chart.categories).toEqual(['Hipótese informada manualmente']);
      const names = (chart.series ?? []).map((series) => series.name);
      expect(names).toContain('Quantidade (hipótese)');
      expect(names).toContain('ITCD (hipótese)');
      expect(names).not.toContain('Quantidade');
      expect(names.some((name) => name.includes('apurado'))).toBeFalse();
      expect((chart.series ?? []).find((series) => series.name === 'ITCD (hipótese)')?.values).toEqual([300]);
      http.verify();
    });

    it('keeps the comparison with public data disabled and never fills a public value', () => {
      const { fixture, page, el, http } = blocked();
      page.uf.set('SP');
      page.quantityInput.set(300);
      page.valueInput.set(5000);
      page.referenceYearInput.set(2022);
      fixture.detectChanges();
      const text = el.textContent as string;
      expect(page.comparisonEnabled()).toBeFalse();
      expect(el.querySelector('[data-testid="comparison-disabled"]')).toBeNull();
      expect(text).not.toContain('Comparação e diferença do imposto');
      expect(text).toContain('Ano da alíquota');
      expect(text).not.toContain('Ano de comparação');
      expect(page.simulatedTaxes().every((row) => row.published === null)).toBeTrue();
      expect(page.hasPublic()).toBeFalse();
      http.verify();
    });

    it('does not print comparison instructions when nothing was informed yet', () => {
      const { el, http } = blocked();
      expect(el.textContent).not.toContain('A comparação com dados públicos está desabilitada');
      expect(el.textContent).not.toContain('Preencha a quantidade');
      http.verify();
    });

    it('offers the requested taxes, operations and goods types', () => {
      const { el, http } = blocked();
      const text = el.textContent as string;
      for (const label of ['ITCD', 'ITBI', 'ISS', 'ICMS']) {
        expect(text).toContain(label);
      }
      expect(text).not.toContain('ICMS (por UF)');
      expect(el.querySelector('select[name="operacao"]')).toBeTruthy();
      expect(text).toContain('Vendas');
      for (const goods of ['Veículos', 'Imóveis', 'Eletrodomésticos', 'Alimentos e Bebidas', 'Outros Bens', 'Serviços Gerais']) {
        expect(text).toContain(goods);
      }
      // O município depende da UF: sem UF, o campo existe mas fica desabilitado.
      const city = el.querySelector('select[name="municipio"]') as HTMLSelectElement;
      expect(city).toBeTruthy();
      expect(city.disabled).toBeTrue();
      expect(text).toContain('Escolha uma UF primeiro');
      http.verify();
    });

    it('leaves ICMS empty when no UF is chosen, without an on-screen rule', () => {
      const { page, el, fixture, http } = blocked();
      page.valueInput.set(1000);
      fixture.detectChanges();
      expect(page.simulatedTaxes().find((row) => row.tax === 'ICMS')?.simulated).toBeNull();
      expect(page.simulatedTaxes().find((row) => row.tax === 'ISS')?.simulated).toBe(50);
      expect(el.textContent).not.toContain('Escolha uma UF para calcular o ICMS');
      page.toggleTax('ICMS', false);
      fixture.detectChanges();
      expect(page.selectedTaxes()).toEqual(['ITCD', 'ITBI', 'ISS']);
      http.verify();
    });

    it('ignores a negative input instead of simulating with it', () => {
      const { fixture, page, el, http } = blocked();
      page.valueInput.set(-5);
      fixture.detectChanges();
      expect(page.hasScenario()).toBeFalse();
      expect(page.inputInvalid()).toBeTrue();
      expect(el.textContent).toContain('Use apenas números iguais ou maiores que zero');
      http.verify();
    });

    it('hides methodology and rule copy', () => {
      const { el, http } = blocked();
      const text = el.textContent as string;
      expect(text).not.toContain('Como é calculado');
      expect(text).not.toContain('Valor de documento não é pagamento');
      expect(text).not.toContain('valores informados por você, tratados como hipótese');
      expect(el.querySelector('[data-testid="rate-note"]')).toBeNull();
      expect(el.querySelector('[data-testid="hypothesis-note"]')).toBeNull();
      http.verify();
    });
  });

  describe('operation filter', () => {
    it('shows operação in the initial filters and not direção', () => {
      const { el, http } = blocked();
      expect(el.querySelector('select[name="operacao"]')).toBeTruthy();
      expect(el.querySelector('[data-testid="direction"]')).toBeNull();
      http.verify();
    });

    it('keeps ICMS on the typed hypothesis', () => {
      const { page, http } = blocked();
      page.uf.set('SP');
      page.valueInput.set(5000);
      expect(page.simulatedTaxes().find((row) => row.tax === 'ICMS')?.simulated).toBe(900);
      http.verify();
    });
  });

  describe('fail closed', () => {
    it('blocks the public data when the reliability block is missing from the answer', () => {
      const { page, el, http } = blocked(ITEMS, null);
      expect(page.publicOpen()).toBeFalse();
      expect(page.items()).toEqual([]);
      expect(el.textContent).toContain('Não foi possível verificar a confiabilidade da fonte');
      expect(el.querySelector('[data-testid="public-blocked"]')).toBeTruthy();
      http.verify();
    });

    it('blocks the public data when one required indicator is not in the block', () => {
      const partial = reliability({
        cgu_nfe_itens_uf_ano: 'CONFERIDO',
      });
      const { page, el, http } = blocked(ITEMS, partial);
      expect(page.publicOpen()).toBeFalse();
      expect(el.querySelector('[data-testid="public-blocked"]')).toBeTruthy();
      expect(page.gate().blocking.some((item) => item.reason.includes('ausente'))).toBeTrue();
      http.verify();
    });

    it('blocks the public data when a single indicator is not CONFERIDO', () => {
      const one = Object.fromEntries(PUBLIC_DATA_INDICATORS.map((id) => [id, 'CONFERIDO'])) as Record<
        string,
        ReliabilityLevel
      >;
      one['cgu_nfe_itens_uf_ano'] = 'NAO_CONFIAVEL';
      const { page, http } = blocked(ITEMS, reliability(one));
      expect(page.publicOpen()).toBeFalse();
      expect(page.gate().blocking.map((item) => item.id)).toEqual(['cgu_nfe_itens_uf_ano']);
      http.verify();
    });

    it('treats EXPLORATORIO as not publishable in the Simulador', () => {
      const { page, el, http } = blocked(ITEMS, reliability('EXPLORATORIO'));
      expect(page.publicOpen()).toBeFalse();
      expect(el.textContent).toContain('Fonte pública EXPLORATORIO');
      http.verify();
    });

    it('blocks the public data and keeps the fields when the read fails', () => {
      const fixture = TestBed.createComponent(SimuladorPageComponent);
      const http = TestBed.inject(HttpTestingController);
      fixture.detectChanges();
      http.expectOne(isProbe).flush('x', { status: 500, statusText: 'err' });
      flushRates(http);
      fixture.detectChanges();
      const el = fixture.nativeElement as HTMLElement;
      expect(fixture.componentInstance.publicOpen()).toBeFalse();
      expect(el.querySelector('[role="alert"]')?.textContent).toContain('não pôde ser verificada');
      expect(el.querySelector('input[name="qtd"]')).toBeTruthy();
      http.verify();
    });
  });

  describe('once the CGU indicators are CONFERIDO', () => {
    it('opens the gate, reads the full data and shows the public data before the fields', () => {
      const { page, el, http } = opened();
      const html = el.innerHTML;
      expect(page.publicOpen()).toBeTrue();
      expect(el.querySelector('[data-testid="public-blocked"]')).toBeNull();
      const publicAt = html.indexOf('Dados públicos e imposto estimado');
      const simulateAt = html.indexOf('Simule com a sua quantidade e valor');
      expect(publicAt).toBeGreaterThan(-1);
      expect(simulateAt).toBeGreaterThan(publicAt);
      page.uf.set('SP');
      expect(page.latest()?.quantity).toBe(200);
      expect(page.latest()?.value).toBe(2000);
      expect(page.taxRows().find((row) => row.tax === 'ITCD')?.amount).toBe(120);
      http.verify();
    });

    it('enables the comparison with the public data again', () => {
      const { fixture, page, el, http } = opened();
      page.uf.set('SP');
      page.quantityInput.set(300);
      page.valueInput.set(5000);
      page.referenceYearInput.set(2022);
      fixture.detectChanges();
      expect(page.comparisonEnabled()).toBeTrue();
      expect(el.textContent).toContain('Comparação e diferença do imposto');
      expect(el.querySelector('[data-testid="comparison-disabled"]')).toBeNull();
      expect(page.comparison().find((row) => row.label === 'Quantidade')?.difference).toBe(100);
      expect(page.chart().categories).toEqual(['2021', '2022', 'Simulado']);
      http.verify();
    });

    it('fills value from public unit price when only quantity is typed', () => {
      const { page, http } = opened();
      page.uf.set('SP');
      page.referenceYearInput.set(2022);
      page.setQuantity(300);
      expect(page.average()).toBe(10);
      expect(page.scenario()).toEqual({ quantity: 300, value: 3000 });
      expect(page.simulatedTaxes().find((row) => row.tax === 'ITCD')?.simulated).toBe(180);
      http.verify();
    });

    it('fills quantity from public unit price when only value is typed', () => {
      const { page, http } = opened();
      page.uf.set('SP');
      page.referenceYearInput.set(2022);
      page.setValue(5000);
      expect(page.scenario()).toEqual({ quantity: 500, value: 5000 });
      expect(page.simulatedTaxes().find((row) => row.tax === 'ITCD')?.simulated).toBe(300);
      http.verify();
    });

    it('rounds derived quantity to whole items instead of a long float', () => {
      const messy = [
        { ano: 2025, uf: 'RJ', itens: 286461, valorItens: '1722385726.16', notas: 1, valorNotas: '1.00' },
      ];
      const { page, http } = opened(messy, [2025]);
      page.uf.set('RJ');
      page.referenceYearInput.set(2025);
      page.setValue(2000000);
      expect(page.quantityShown()).toBe(333);
      expect(page.valueShown()).toBe(2000000);
      expect(String(page.quantityShown())).not.toContain('332.6328076796769');
      http.verify();
    });

    it('shows large scenario taxes in compact form so the KPI cards fit', () => {
      const { page, fixture, el, http } = opened();
      page.uf.set('SP');
      page.setValue(12_025_272_033.33);
      fixture.detectChanges();
      const itcd = Array.from(el.querySelectorAll('app-kpi-card')).find((card) =>
        card.textContent?.includes('ITCD do cenário'),
      )?.textContent;
      expect(itcd).toContain('R$ 721,5 mi');
      expect(itcd).not.toContain('721.516.322');
      http.verify();
    });
  });

  describe('hypothesis labelling', () => {
    // Negações que o texto da tela usa de propósito.
    const NEGATIONS = [
      /não é imposto apurado nem devido/gi,
      /não é apuração fiscal/gi,
      /nem apuração/gi,
      /simulador_imposto_apurado_dados_publicos/g, // identificador técnico do indicador, não texto da tela
    ];
    const withoutNegations = (text: string): string => NEGATIONS.reduce((acc, rx) => acc.replace(rx, ''), text);

    it('never presents a simulated value as assessed or due tax (public gate closed)', () => {
      const { fixture, page, el, http } = blocked();
      page.setUf('SP');
      page.quantityInput.set(10);
      page.valueInput.set(1000);
      fixture.detectChanges();
      http.expectOne('/ibge-municipios.json').flush({ municipios: [] });
      fixture.detectChanges();
      const text = withoutNegations(el.textContent as string);
      expect(text).not.toMatch(/apurad|devid/i);
      expect(el.textContent).toContain('Hipótese informada manualmente');
      expect(el.querySelector('[data-testid="hypothesis-note"]')).toBeNull();
      http.verify();
    });

    it('never presents a public-data estimate as assessed or due tax (public gate open)', () => {
      const { fixture, page, el, http } = opened();
      page.setUf('SP');
      page.valueInput.set(1000);
      fixture.detectChanges();
      http.expectOne('/ibge-municipios.json').flush({ municipios: [] });
      fixture.detectChanges();
      expect(withoutNegations(el.textContent as string)).not.toMatch(/apurad|devid/i);
      const names = [...(page.chart().series ?? []), ...(page.publicChart().series ?? [])].map((series) => series.name);
      expect(names.some((name) => /apurad|devid/i.test(name))).toBeFalse();
      http.verify();
    });

  });

  describe('rates', () => {
    function acreBlocked(years: number[]) {
      const fixture = TestBed.createComponent(SimuladorPageComponent);
      const http = TestBed.inject(HttpTestingController);
      fixture.detectChanges();
      http.expectOne(isProbe).flush(view([], { years }));
      flushRates(http);
      const page = fixture.componentInstance;
      page.uf.set('AC');
      fixture.detectChanges();
      return { fixture, page, http, el: fixture.nativeElement as HTMLElement };
    }

    it('marks the Acre modal rate as Validado and every other rate as pending legal validation', () => {
      const { fixture, page, el, http } = acreBlocked([2022, 2023, 2024]);
      page.valueInput.set(1000);
      fixture.detectChanges();
      expect(page.resolved('ICMS', 2022)).toEqual(jasmine.objectContaining({ rate: 17, status: 'VALIDADO' }));
      expect(page.resolved('ICMS', 2024)).toEqual(jasmine.objectContaining({ rate: 19, status: 'VALIDADO' }));
      expect(page.resolved('ITCD', 2024)).toEqual(jasmine.objectContaining({ rate: 6, status: 'PENDENTE' }));
      const text = el.textContent as string;
      expect(text).toContain('19%');
      expect(text).toContain('6%');
      expect(text).not.toContain('Validado');
      expect(text).not.toContain('Parâmetro de simulação');
      expect(page.resolved('ITCD', 2024).isSimulation).toBeTrue();
      expect(page.resolved('ICMS', 2024).isSimulation).toBeFalse();
      expect(text).not.toContain('exceções por mercadoria e operação não estão modeladas');
      http.verify();
    });

    it('never treats a municipality or operation rate as the rate of the whole UF', () => {
      const { page, http } = acreBlocked([2024]);
      const city = { ...flat('ITBI', 2), uf: 'AC', jurisdictionLevel: 'MUNICIPIO', municipalityIbgeCode: '1200401' };
      page.rateVersions.set([...RATES, city] as unknown as RateVersion[]);
      expect(page.resolved('ITBI', 2024).rate).toBe(3);
      expect(page.resolved('ITBI', 2024).isSimulation).toBeTrue();
      http.verify();
    });

    it('never presents the rate table as homologated, even for the validated Acre rate', () => {
      const { page, el, http } = acreBlocked([2024]);
      page.valueInput.set(1000);
      page.referenceYearInput.set(2024);
      const text = el.textContent as string;
      expect(text).not.toContain('Nenhuma tabela de alíquotas está homologada');
      expect(text).not.toContain('Homologado: sim');
      expect(page.resolved('ICMS', 2024).status).toBe('VALIDADO');
      http.verify();
    });

    it('leaves the 2023 Acre tax empty because the validated rate changed on April first', () => {
      const { fixture, page, http } = acreBlocked([2023]);
      page.valueInput.set(2000);
      page.referenceYearInput.set(2023);
      fixture.detectChanges();
      const icms = page.simulatedTaxes().find((row) => row.tax === 'ICMS');
      expect(icms?.simulated).toBeNull();
      expect(icms?.resolved.changedWithinYear).toBeTrue();
      expect((fixture.nativeElement as HTMLElement).textContent).toContain('muda no ano');
      http.verify();
    });

    it('falls back to pending rates and says so when the rate table cannot be read', () => {
      const fixture = TestBed.createComponent(SimuladorPageComponent);
      const http = TestBed.inject(HttpTestingController);
      fixture.detectChanges();
      http.expectOne(isProbe).flush(view([]));
      flushRates(http, 'error');
      const page = fixture.componentInstance;
      page.uf.set('AC');
      fixture.detectChanges();
      expect(page.ratesFallback()).toBeTrue();
      expect(page.resolved('ICMS', 2024)).toEqual(jasmine.objectContaining({ rate: 19, status: 'PENDENTE' }));
      expect((fixture.nativeElement as HTMLElement).textContent).not.toContain('A tabela de alíquotas não pôde ser lida');
      http.verify();
    });
  });
});

describe('SimuladorPageComponent opened from the SPED panel', () => {
  function open(query: Record<string, string>) {
    TestBed.configureTestingModule({
      imports: [SimuladorPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: ActivatedRoute, useValue: { snapshot: { queryParamMap: convertToParamMap(query) } } },
      ],
    });
    const fixture = TestBed.createComponent(SimuladorPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(isProbe).flush(view([]));
    flushRates(http);
    fixture.detectChanges();
    return { page: fixture.componentInstance, http };
  }

  it('pre-fills the UF and operação from the URL', () => {
    const { page, http } = open({ uf: 'SP', operacao: 'Compras' });
    expect(page.uf()).toBe('SP');
    expect(page.operation()).toBe('Compras');
    http.expectOne('/ibge-municipios.json').flush({ municipios: [] });
    http.verify();
  });

  it('ignores unknown values in the URL', () => {
    const { page, http } = open({ uf: 'XX', operacao: '<img src=x>' });
    expect(page.uf()).toBe('');
    expect(page.operation()).toBe('Vendas');
    http.verify();
  });
});

describe('SimuladorPageComponent municipality', () => {
  const CITIES = [
    { uf: 'AC', ibge: '1200401', nome: 'Rio Branco' },
    { uf: 'AC', ibge: '1200013', nome: 'Acrelândia' },
    { uf: 'SP', ibge: '3550308', nome: 'São Paulo' },
  ];
  const cityRate = (tax: string, rate: number, ibge: string) => ({
    ...flat(tax, rate),
    uf: 'AC',
    jurisdictionLevel: 'MUNICIPIO',
    municipalityIbgeCode: ibge,
    status: 'PENDENTE',
  });

  function start(rates: unknown[] = RATES) {
    TestBed.configureTestingModule({
      imports: [SimuladorPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    const fixture = TestBed.createComponent(SimuladorPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(isProbe).flush(view([]));
    flushRates(http, rates);
    fixture.detectChanges();
    return { fixture, http, page: fixture.componentInstance, el: fixture.nativeElement as HTMLElement };
  }

  function select(fixture: { detectChanges(): void }, el: HTMLElement, name: string, value: string): void {
    const field = el.querySelector(`select[name="${name}"]`) as HTMLSelectElement;
    field.value = value;
    field.dispatchEvent(new Event('change'));
    fixture.detectChanges();
  }

  it('does not read the municipality list until a UF is chosen', () => {
    const { http } = start();
    http.expectNone('/ibge-municipios.json');
    http.verify();
  });

  it('lists only the municipalities of the chosen UF, in alphabetical order', async () => {
    const { fixture, http, page, el } = start();
    page.setUf('AC');
    fixture.detectChanges();
    http.expectOne('/ibge-municipios.json').flush({ municipios: CITIES });
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
    expect(page.municipalityOptions().map((city) => city.nome)).toEqual(['Acrelândia', 'Rio Branco']);
    const field = el.querySelector('select[name="municipio"]') as HTMLSelectElement;
    expect(field.disabled).toBeFalse();
    expect(Array.from(field.options).map((option) => option.text)).not.toContain('São Paulo');
    http.verify();
  });

  it('reads the list once, even when the UF changes', () => {
    const { fixture, http, page } = start();
    page.setUf('AC');
    fixture.detectChanges();
    http.expectOne('/ibge-municipios.json').flush({ municipios: CITIES });
    page.setUf('SP');
    fixture.detectChanges();
    http.expectNone('/ibge-municipios.json');
    http.verify();
  });

  it('clears the municipality when the UF changes and refuses a code from another UF', () => {
    const { fixture, http, page, el } = start();
    page.setUf('AC');
    fixture.detectChanges();
    http.expectOne('/ibge-municipios.json').flush({ municipios: CITIES });
    page.setMunicipality('1200401');
    expect(page.municipalityOrNull()).toBe('1200401');
    page.setUf('SP');
    expect(page.municipality()).toBe('');
    expect(page.municipalityOrNull()).toBeNull();
    page.setMunicipality('1200401');
    expect(page.municipalityOrNull()).toBeNull();
    page.setMunicipality('<script>');
    expect(page.municipality()).toBe('');
    http.verify();
  });

  it('uses a registered municipal ITBI rate only for that municipality, never for the whole UF', () => {
    const { fixture, http, page, el } = start([...RATES, cityRate('ITBI', 2, '1200401')]);
    page.setUf('AC');
    fixture.detectChanges();
    http.expectOne('/ibge-municipios.json').flush({ municipios: CITIES });
    expect(page.resolved('ITBI', 2024).rate).toBe(3);
    expect(page.resolved('ITBI', 2024).isSimulation).toBeTrue();
    page.setMunicipality('1200013');
    expect(page.resolved('ITBI', 2024).rate).toBe(3);
    page.setMunicipality('1200401');
    expect(page.resolved('ITBI', 2024).rate).toBe(2);
    expect(page.resolved('ITBI', 2024).isSimulation).toBeFalse();
    expect(page.resolved('ISS', 2024).rate).toBe(5);
    http.verify();
  });

  it('says that no municipal rate is registered and keeps ITBI and ISS as simulation parameters', () => {
    const { fixture, http, page, el } = start();
    page.setUf('AC');
    fixture.detectChanges();
    http.expectOne('/ibge-municipios.json').flush({ municipios: CITIES });
    page.setMunicipality('1200401');
    fixture.detectChanges();
    expect(el.querySelector('[data-testid="municipality-note"]')).toBeNull();
    expect(page.resolved('ITBI', 2024).isSimulation).toBeTrue();
    expect(page.rateMeta(page.resolved('ISS', 2024), 2024)).toBe('5%');
    http.verify();
  });

  it('keeps working by UF when the municipality list cannot be read', () => {
    const { fixture, http, page, el } = start();
    page.setUf('AC');
    fixture.detectChanges();
    http.expectOne('/ibge-municipios.json').flush('x', { status: 404, statusText: 'nf' });
    fixture.detectChanges();
    expect(el.querySelector('[data-testid="municipality-error"]')).toBeTruthy();
    expect((el.querySelector('select[name="municipio"]') as HTMLSelectElement).disabled).toBeTrue();
    page.valueInput.set(1000);
    expect(page.resolved('ICMS', 2024).rate).toBe(19);
    http.verify();
  });
});

describe('SimuladorPageComponent functional flow through the DOM (homologação)', () => {
  const CITIES = [
    { uf: 'AC', ibge: '1200401', nome: 'Rio Branco' },
    { uf: 'SP', ibge: '3550308', nome: 'São Paulo' },
  ];

  async function start() {
    TestBed.configureTestingModule({
      imports: [SimuladorPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    const fixture = TestBed.createComponent(SimuladorPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne(isProbe).flush(view([]));
    flushRates(http);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
    const el = fixture.nativeElement as HTMLElement;
    const field = <T extends HTMLElement>(name: string) => el.querySelector(`[name="${name}"]`) as T;
    const choose = async (name: string, value: string) => {
      const select = field<HTMLSelectElement>(name);
      select.value = value;
      select.dispatchEvent(new Event('change'));
      fixture.detectChanges();
      await fixture.whenStable();
      fixture.detectChanges();
    };
    const type = async (name: string, value: string) => {
      const input = field<HTMLInputElement>(name);
      input.value = value;
      input.dispatchEvent(new Event('input'));
      fixture.detectChanges();
      await fixture.whenStable();
      fixture.detectChanges();
    };
    const kpi = (tax: string): string =>
      Array.from(el.querySelectorAll('app-kpi-card'))
        .find((card) => card.textContent?.includes(`${tax} do cenário`))
        ?.textContent?.replace(/\s+/g, ' ') ?? '';
    return { fixture, http, page: fixture.componentInstance, el, field, choose, type, kpi };
  }

  it('walks the whole form: UF, municipality, taxes, operation, goods, quantity and value', async () => {
    const { fixture, http, page, el, field, choose, type, kpi } = await start();
    await choose('uf', 'AC');
    http.expectOne('/ibge-municipios.json').flush({ municipios: CITIES });
    fixture.detectChanges();
    await choose('municipio', '1200401');
    await choose('operacao', 'Compras');
    await choose('tipo', 'Veículos');
    await type('qtd', '3');
    await type('valor', '1000');
    expect([page.uf(), page.municipality(), page.operation(), page.goods()]).toEqual([
      'AC',
      '1200401',
      'Compras',
      'Veículos',
    ]);
    expect(page.scenario()).toEqual({ quantity: 3, value: 1000 });
    // Cada imposto é calculado sobre o valor informado e nunca somado aos demais.
    expect(kpi('ITCD')).toContain('R$ 60,00');
    expect(kpi('ITBI')).toContain('R$ 30,00');
    expect(kpi('ISS')).toContain('R$ 50,00');
    // O ano da alíquota padrão é 2022 (último ano da lista): o ICMS do Acre vigente era 17%.
    expect(kpi('ICMS')).toContain('R$ 170,00');
    expect(el.textContent).not.toMatch(/total dos impostos/i);
    expect(field<HTMLSelectElement>('municipio').disabled).toBeFalse();
    http.verify();
  });

  it('updates the chart as soon as the value changes', async () => {
    const { http, page, type } = await start();
    await type('valor', '1000');
    const before = page.chart().series?.find((series) => series.name === 'ISS (hipótese)')?.values;
    expect(before).toEqual([50]);
    await type('valor', '2000');
    expect(page.chart().series?.find((series) => series.name === 'ISS (hipótese)')?.values).toEqual([100]);
    await type('valor', '');
    expect(page.chart().series?.find((series) => series.name === 'ISS (hipótese)')?.values).toEqual([null]);
    http.verify();
  });

  it('keeps decimal precision typed in the field', async () => {
    const { http, page, type, kpi } = await start();
    await type('valor', '4.06');
    page.selectedTaxes.set(['ITCD', 'ITBI', 'ISS', 'ICMS']);
    expect(page.simulatedTaxes().find((row) => row.tax === 'ISS')?.simulated).toBe(0.2);
    await type('valor', '1234567.89');
    expect(kpi('ISS')).toContain('R$ 61.728,39');
    http.verify();
  });

  it('shows nothing for an empty field and treats zero as zero, not as missing', async () => {
    const { http, page, type, kpi } = await start();
    await type('valor', '');
    expect(page.hasScenario()).toBeFalse();
    await type('valor', '0');
    expect(page.hasScenario()).toBeTrue();
    expect(kpi('ISS')).toContain('R$ 0,00');
    expect(kpi('ISS')).not.toContain('-R$');
    http.verify();
  });

  it('ignores negative, exponent and absurd entries and says so, without computing a tax', async () => {
    const { http, page, el, type } = await start();
    await type('valor', '-100');
    expect(page.scenario().value).toBeNull();
    expect(page.inputInvalid()).toBeTrue();
    expect(el.querySelector('[role="alert"]')?.textContent).toContain('Use apenas números iguais ou maiores que zero');
    await type('qtd', '-1');
    expect(page.scenario().quantity).toBeNull();
    // Valor acima do que um número de ponto flutuante representa ao centavo: imposto em branco.
    await type('valor', '1e300');
    expect(page.simulatedTaxes().every((row) => row.simulated === null)).toBeTrue();
    http.verify();
  });

  it('handles very large quantities and values without scientific notation or infinity', async () => {
    const { http, page, el, type } = await start();
    await type('qtd', '9007199254740991');
    await type('valor', '100000000000');
    expect(page.scenario()).toEqual({ quantity: 9007199254740991, value: 100000000000 });
    expect(page.simulatedTaxes().find((row) => row.tax === 'ISS')?.simulated).toBe(5000000000);
    expect(el.textContent).not.toMatch(/Infinity|NaN|e\+\d/);
    http.verify();
  });

  it('drops a taxes selection and recalculates without it', async () => {
    const { http, page, type, kpi, fixture, el } = await start();
    await type('valor', '1000');
    const iss = el.querySelector('input[name="tax-ISS"]') as HTMLInputElement;
    iss.checked = false;
    iss.dispatchEvent(new Event('change'));
    fixture.detectChanges();
    expect(page.selectedTaxes()).not.toContain('ISS');
    expect(kpi('ISS')).toBe('');
    expect(page.chart().series?.some((series) => series.name.startsWith('ISS'))).toBeFalse();
    http.verify();
  });

  it('does not overflow horizontally on a narrow phone screen', async () => {
    const { fixture, http, el } = await start();
    const host = fixture.nativeElement as HTMLElement;
    host.style.display = 'block';
    host.style.width = '320px';
    host.style.overflowX = 'visible';
    fixture.detectChanges();
    const form = el.querySelector('form.filters') as HTMLElement;
    expect(form.getBoundingClientRect().width).toBeLessThanOrEqual(320);
    for (const control of Array.from(el.querySelectorAll('select, input[type="number"]'))) {
      expect((control as HTMLElement).getBoundingClientRect().right).toBeLessThanOrEqual(321);
    }
    http.verify();
  });

  it('keeps every control reachable by label for keyboard and screen reader users', async () => {
    const { http, el } = await start();
    const controls = Array.from(el.querySelectorAll('select, input'));
    expect(controls.length).toBeGreaterThanOrEqual(9);
    for (const control of controls) {
      expect(control.closest('label') ?? control.getAttribute('aria-label')).toBeTruthy();
    }
    http.verify();
  });
});