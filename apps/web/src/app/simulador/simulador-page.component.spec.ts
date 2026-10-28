import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { APP_NAV_GROUPS, OPEN_NAV_GROUP_IDS } from '../layout/navigation';
import { PUBLIC_DATA_INDICATORS, ReliabilityBlock, ReliabilityLevel } from '../shared/reliability/indicator-reliability';
import { RateVersion } from './simulador-aliquotas';
import { SimuladorPageComponent } from './simulador-page.component';

const OPERATIONS = [
  'Compras',
  'Vendas',
  'Transferências',
  'Doações / bonificações / brindes',
  'Serviços Prestados',
  'Serviços Tomados',
  'Outras Saídas',
];

const run = {
  runId: '0b7a8d0e-0000-4000-8000-000000000002',
  checksum: 'cd'.repeat(32),
  layoutVersion: 'sped-nfe-uf-cfop-v1',
  competence: '2021-25',
  loadedAt: '2026-10-27T12:00:00+00:00',
  receivedCount: 3,
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
        evidence: [],
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
    sourceId: 'SPED-NFE-UF-CFOP',
    valueKind: 'ESTIMATED_ALLOCATION',
    banner: 'Base exploratória, não homologada. O valor por UF é rateio estimado.',
    formula: 'Valor nacional do CFOP × participação da UF',
    homologated: false,
    published: false,
    createsTaxCredit: false,
    ...(block ? { reliability: block } : {}),
    level: 'SERIE',
    page: 1,
    pageSize: 1000,
    total: items.length,
    years,
    operations: OPERATIONS,
    ufs: ['AC', 'SP'],
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
  { ano: 2021, uf: 'SP', operacao: 'Vendas', quantidade: 100, valorEstimado: '1000.00' },
  { ano: 2022, uf: 'SP', operacao: 'Vendas', quantidade: 200, valorEstimado: '2000.00' },
  { ano: 2022, uf: 'SP', operacao: 'Compras', quantidade: 999, valorEstimado: '9999.00' },
];

const isProbe = (req: { url: string; params: { get(name: string): string | null } }) =>
  req.url === '/v1/sped-operacoes' && req.params.get('pageSize') === '1';
const isFullRead = (req: { url: string; params: { get(name: string): string | null } }) =>
  req.url === '/v1/sped-operacoes' && req.params.get('pageSize') === '1000';

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

  describe('with the SPED source NAO_CONFIAVEL (today)', () => {
    it('blocks the public data and says why, without rendering any SPED number', () => {
      const { page, el, http } = blocked();
      const text = el.textContent as string;
      expect(page.publicOpen()).toBeFalse();
      expect(el.querySelector('[data-testid="public-blocked"]')).toBeTruthy();
      expect(text).toContain('Fonte SPED NAO_CONFIAVEL: indicadores não são usados no Simulador');
      expect(text).toContain('O que falta para liberar');
      expect(text).toContain('Motivo de sped_compras_uf');
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
      expect(el.querySelector('[data-testid="hypothesis-note"]')?.textContent).toContain('Hipótese informada manualmente');
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
      expect(el.querySelector('[data-testid="comparison-disabled"]')?.textContent).toContain('Comparação desabilitada');
      expect(text).not.toContain('Comparação e diferença do imposto');
      expect(text).toContain('Ano da alíquota');
      expect(text).not.toContain('Ano de comparação');
      expect(page.simulatedTaxes().every((row) => row.published === null)).toBeTrue();
      expect(page.hasPublic()).toBeFalse();
      http.verify();
    });

    it('tells the user what to type when nothing was informed yet', () => {
      const { el, http } = blocked();
      expect(el.textContent).toContain('A comparação com dados públicos está desabilitada');
      http.verify();
    });

    it('offers the requested taxes, operations and goods types', () => {
      const { el, http } = blocked();
      const text = el.textContent as string;
      for (const label of ['ITCD', 'ITBI', 'ISS', 'ICMS (por UF)']) {
        expect(text).toContain(label);
      }
      for (const operation of OPERATIONS) {
        expect(text).toContain(operation);
      }
      for (const goods of ['Veículos', 'Imóveis', 'Eletrodomésticos', 'Alimentos e Bebidas', 'Outros Bens', 'Serviços Gerais']) {
        expect(text).toContain(goods);
      }
      expect(el.querySelector('select[name="municipio"]')).toBeNull();
      expect(text).not.toContain('Município');
      http.verify();
    });

    it('leaves ICMS empty and warns when no UF is chosen', () => {
      const { page, el, fixture, http } = blocked();
      page.valueInput.set(1000);
      fixture.detectChanges();
      expect(page.simulatedTaxes().find((row) => row.tax === 'ICMS')?.simulated).toBeNull();
      expect(page.simulatedTaxes().find((row) => row.tax === 'ISS')?.simulated).toBe(50);
      expect(el.textContent).toContain('Escolha uma UF para calcular o ICMS');
      page.toggleTax('ICMS', false);
      fixture.detectChanges();
      expect(page.selectedTaxes()).toEqual(['ITCD', 'ITBI', 'ISS']);
      expect(el.textContent).not.toContain('Escolha uma UF para calcular o ICMS');
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

    it('uses the public-data free banner instead of the SPED banner', () => {
      const { el, http } = blocked();
      expect(el.textContent).toContain('valores informados por você, tratados como hipótese');
      expect(el.textContent).not.toContain('Base exploratória, não homologada');
      http.verify();
    });
  });

  describe('transfers', () => {
    it('offers a direction only for Transferências and resets it when the operation changes', () => {
      const { fixture, page, el, http } = blocked();
      expect(el.querySelector('[data-testid="direction"]')).toBeNull();
      page.setOperation('Transferências');
      fixture.detectChanges();
      expect(el.querySelector('[data-testid="direction"]')).toBeTruthy();
      expect(el.querySelector('[data-testid="transfer-note"]')?.textContent).toContain('nunca são somadas');
      page.transferDirection.set('RECEBIDA');
      page.icmsTransferOptIn.set(true);
      page.setOperation('Vendas');
      expect(page.transferDirection()).toBe('');
      expect(page.icmsTransferOptIn()).toBeFalse();
      http.verify();
    });

    it('does not apply ICMS to a transfer unless the user opts in, as a hypothesis', () => {
      const { fixture, page, el, http } = blocked();
      page.uf.set('SP');
      page.setOperation('Transferências');
      page.valueInput.set(5000);
      fixture.detectChanges();
      const icms = page.simulatedTaxes().find((row) => row.tax === 'ICMS');
      expect(icms?.blocked).toBeTrue();
      expect(icms?.simulated).toBeNull();
      expect(page.simulatedTaxes().find((row) => row.tax === 'ITCD')?.simulated).toBe(300);
      expect(page.activeTaxes()).not.toContain('ICMS');
      expect((page.chart().series ?? []).map((series) => series.name)).not.toContain('ICMS (hipótese)');
      expect(el.textContent).toContain('ICMS não calculado');

      page.icmsTransferOptIn.set(true);
      fixture.detectChanges();
      expect(page.simulatedTaxes().find((row) => row.tax === 'ICMS')?.simulated).toBe(900);
      expect(page.activeTaxes()).toContain('ICMS');
      expect(el.textContent).toContain('hipótese informada por você (equiparação optada)');
      http.verify();
    });

    it('keeps ICMS for other operations', () => {
      const { page, http } = blocked();
      page.uf.set('SP');
      page.valueInput.set(5000);
      expect(page.simulatedTaxes().find((row) => row.tax === 'ICMS')?.simulated).toBe(900);
      http.verify();
    });

    it('never mixes the two directions in public data (future homologated base)', () => {
      const both = [
        { ano: 2021, uf: 'SP', operacao: 'Transferências', quantidade: 10, valorEstimado: '100.00', direcao: 'REMETIDA' },
        { ano: 2021, uf: 'SP', operacao: 'Transferências', quantidade: 5, valorEstimado: '50.00', direcao: 'RECEBIDA' },
      ];
      const { page, http } = opened(both, [2021]);
      page.uf.set('SP');
      page.setOperation('Transferências');
      // Sem direção escolhida nada entra: somar as duas duplicaria a contagem.
      expect(page.items()).toEqual([]);
      expect(page.latest()?.quantity).toBeNull();
      page.transferDirection.set('REMETIDA');
      expect(page.latest()?.quantity).toBe(10);
      page.transferDirection.set('RECEBIDA');
      expect(page.latest()?.quantity).toBe(5);
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
        sped_quantidade_uf_cfop_ano: 'CONFERIDO',
        sped_compras_uf: 'CONFERIDO',
        sped_valor_estimado_uf_cfop_ano: 'CONFERIDO',
        sped_valor_estimado_operacao: 'CONFERIDO',
      });
      const { page, el, http } = blocked(ITEMS, partial);
      expect(page.publicOpen()).toBeFalse();
      expect(el.textContent).toContain('Indicador ausente da resposta da API');
      http.verify();
    });

    it('blocks the public data when a single indicator is not CONFERIDO', () => {
      const one = Object.fromEntries(PUBLIC_DATA_INDICATORS.map((id) => [id, 'CONFERIDO'])) as Record<
        string,
        ReliabilityLevel
      >;
      one['sped_compras_uf'] = 'NAO_CONFIAVEL';
      const { page, http } = blocked(ITEMS, reliability(one));
      expect(page.publicOpen()).toBeFalse();
      expect(page.gate().blocking.map((item) => item.id)).toEqual(['sped_compras_uf']);
      http.verify();
    });

    it('treats EXPLORATORIO as not publishable in the Simulador', () => {
      const { page, el, http } = blocked(ITEMS, reliability('EXPLORATORIO'));
      expect(page.publicOpen()).toBeFalse();
      expect(el.textContent).toContain('Fonte SPED EXPLORATORIO');
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

  describe('once every indicator is CONFERIDO (future homologated base)', () => {
    it('opens the gate, reads the full data and shows the public data before the fields', () => {
      const { page, el, http } = opened();
      const html = el.innerHTML;
      expect(page.publicOpen()).toBeTrue();
      expect(el.querySelector('[data-testid="public-blocked"]')).toBeNull();
      const publicAt = html.indexOf('Dados públicos e imposto apurado');
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
      expect(text).toContain('Alíquota 19% · Validado');
      expect(text).toContain('Alíquota 6% · Parâmetro de simulação, não é alíquota da UF nem do município');
      expect(page.resolved('ITCD', 2024).isSimulation).toBeTrue();
      expect(page.resolved('ICMS', 2024).isSimulation).toBeFalse();
      expect(text).toContain('exceções por mercadoria e operação não estão modeladas');
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
      expect(text).toContain('Nenhuma tabela de alíquotas está homologada');
      expect(text).toContain('nenhuma tabela está homologada');
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
      expect((fixture.nativeElement as HTMLElement).textContent).toContain('mudou em 2023');
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
      expect((fixture.nativeElement as HTMLElement).textContent).toContain('A tabela de alíquotas não pôde ser lida');
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

  it('pre-fills the UF and the operation from the URL', () => {
    const { page, http } = open({ uf: 'SP', operacao: 'Compras' });
    expect(page.uf()).toBe('SP');
    expect(page.operation()).toBe('Compras');
    http.verify();
  });

  it('ignores unknown values in the URL', () => {
    const { page, http } = open({ uf: 'XX', operacao: '<img src=x>' });
    expect(page.uf()).toBe('');
    expect(page.operation()).toBe('Vendas');
    http.verify();
  });
});
