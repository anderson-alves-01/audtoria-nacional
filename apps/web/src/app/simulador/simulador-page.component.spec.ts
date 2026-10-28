import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { APP_NAV_GROUPS, OPEN_NAV_GROUP_IDS } from '../layout/navigation';
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

function view(items: unknown[], withRun = true, years = [2021, 2022]): Record<string, unknown> {
  return {
    sourceId: 'SPED-NFE-UF-CFOP',
    valueKind: 'ESTIMATED_ALLOCATION',
    banner: 'Base exploratória, não homologada. O valor por UF é rateio estimado.',
    formula: 'Valor nacional do CFOP × participação da UF',
    homologated: false,
    published: false,
    createsTaxCredit: false,
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

describe('SimuladorPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SimuladorPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();
  });

  function loaded(items: unknown[] = ITEMS, withRun = true) {
    const fixture = TestBed.createComponent(SimuladorPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne((req) => req.url === '/v1/sped-operacoes' && req.params.get('level') === 'SERIE').flush(view(items, withRun));
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

  it('keeps the simulation fields usable even when no public data was loaded', () => {
    const { page, fixture, el, http } = loaded([], false);
    expect(el.textContent).toContain('Simulação · não é apuração fiscal');
    expect(el.textContent).toContain('Ainda não há carga validada do SPED');
    expect(el.textContent).not.toContain('Dados públicos e imposto apurado');
    expect(el.querySelector('input[name="qtd"]')).toBeTruthy();
    expect(el.querySelector('input[name="valor"]')).toBeTruthy();
    page.uf.set('SP');
    page.valueInput.set(1000);
    fixture.detectChanges();
    // Simulated tax still works (value x rate); the public side stays empty.
    const itcd = page.simulatedTaxes().find((row) => row.tax === 'ITCD');
    expect(itcd?.simulated).toBe(60);
    expect(itcd?.published).toBeNull();
    const valueRow = page.comparison().find((row) => row.label === 'Valor');
    expect(valueRow?.publicValue).toBeNull();
    expect(valueRow?.difference).toBeNull();
    expect(el.textContent).toContain('Comparação e diferença do imposto');
    http.verify();
  });

  it('shows the public data first, then the quantity and value fields, with no "Parte A/B" text', () => {
    const { el, http } = loaded();
    const html = el.innerHTML;
    expect(el.querySelector('input[name="qtd"]')).toBeTruthy();
    expect(el.querySelector('input[name="valor"]')).toBeTruthy();
    expect((el.querySelector('input[name="qtd"]') as HTMLInputElement).placeholder).toContain('Ex.');
    const publicAt = html.indexOf('Dados públicos e imposto apurado');
    const simulateAt = html.indexOf('Simule com a sua quantidade e valor');
    expect(publicAt).toBeGreaterThan(-1);
    expect(simulateAt).toBeGreaterThan(publicAt);
    expect(el.textContent).not.toContain('Parte A');
    expect(el.textContent).not.toContain('Parte B');
    expect(el.textContent).toContain('Preencha a quantidade, o valor ou ambos');
    http.verify();
  });

  it('shows the simulated tax of each chosen tax as soon as a value is typed', async () => {
    const { fixture, page, el, http } = loaded();
    page.uf.set('SP');
    fixture.detectChanges();
    await fixture.whenStable();
    const value = el.querySelector('input[name="valor"]') as HTMLInputElement;
    value.value = '5000';
    value.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    expect(page.valueInput()).toBe(5000);
    expect(page.simulatedTaxes().find((row) => row.tax === 'ITCD')?.simulated).toBe(300);
    expect(page.simulatedTaxes().find((row) => row.tax === 'ICMS')?.simulated).toBe(900);
    expect(el.textContent).toContain('ITCD do cenário');
    expect(el.textContent).not.toContain('Preencha a quantidade, o valor ou ambos');
    http.verify();
  });

  it('offers the requested taxes, operations and goods types', () => {
    const { el, http } = loaded();
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

  it('shows value, quantity, operation and tax for one operation without mixing others', () => {
    const { fixture, page, el, http } = loaded();
    page.uf.set('SP');
    fixture.detectChanges();
    const text = el.textContent as string;
    expect(text).toContain('Dados públicos e imposto apurado');
    expect(text).toContain('ITCD apurado');
    // Vendas 2022 SP: 200 and R$ 2.000,00 -> ITCD 6% = R$ 120,00. Compras (999) never appears.
    expect(page.latest()?.quantity).toBe(200);
    expect(page.latest()?.value).toBe(2000);
    expect(page.taxRows().find((row) => row.tax === 'ITCD')?.amount).toBe(120);
    expect(page.taxRows().find((row) => row.tax === 'ICMS')?.amount).toBe(360);
    expect(text).not.toContain('999');
    expect(el.querySelectorAll('tbody tr').length).toBe(2);
    http.verify();
  });

  it('leaves ICMS empty and warns when no UF is chosen', () => {
    const { page, el, fixture, http } = loaded();
    expect(page.taxRows().find((row) => row.tax === 'ICMS')?.amount).toBeNull();
    expect(page.taxRows().find((row) => row.tax === 'ISS')?.amount).toBe(100);
    expect(el.textContent).toContain('Escolha uma UF para calcular o ICMS');
    page.toggleTax('ICMS', false);
    fixture.detectChanges();
    expect(page.selectedTaxes()).toEqual(['ITCD', 'ITBI', 'ISS']);
    expect(el.textContent).not.toContain('Escolha uma UF para calcular o ICMS');
    http.verify();
  });

  it('Part B: compares the desired quantity and value with the public data and the tax difference', () => {
    const { fixture, page, el, http } = loaded();
    page.uf.set('SP');
    expect(el.textContent).not.toContain('Comparação e diferença do imposto');
    page.quantityInput.set(300);
    page.valueInput.set(5000);
    page.referenceYearInput.set(2022);
    fixture.detectChanges();
    const text = el.textContent as string;
    expect(text).toContain('Comparação e diferença do imposto');
    expect(el.querySelectorAll('app-bi-chart').length).toBe(2);
    const rows = page.comparison();
    expect(rows.find((row) => row.label === 'Quantidade')?.difference).toBe(100);
    expect(rows.find((row) => row.label.startsWith('ITCD'))?.difference).toBe(180);
    expect(page.chart().categories).toEqual(['2021', '2022', 'Simulado']);
    http.verify();
  });

  it('ignores a negative input instead of simulating with it', () => {
    const { fixture, page, el, http } = loaded();
    page.valueInput.set(-5);
    fixture.detectChanges();
    expect(page.hasScenario()).toBeFalse();
    expect(page.inputInvalid()).toBeTrue();
    expect(el.textContent).toContain('Use apenas números iguais ou maiores que zero');
    http.verify();
  });

  it('warns that the source is under review and not reliable for fiscal use', () => {
    const { el, http } = loaded();
    const note = el.querySelector('[data-testid="reliability"]');
    expect(note?.textContent).toContain('Fonte em revisão');
    expect(note?.textContent).toContain('Não use como referência fiscal');
    http.verify();
  });

  it('marks the Acre modal rate as Validado and every other rate as pending legal validation', () => {
    const acItems = [2022, 2023, 2024].map((ano) => ({
      ano, uf: 'AC', operacao: 'Vendas', quantidade: 10, valorEstimado: '1000.00',
    }));
    const fixture = TestBed.createComponent(SimuladorPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne((req) => req.params.get('level') === 'SERIE').flush(view(acItems, true, [2022, 2023, 2024]));
    flushRates(http);
    const page = fixture.componentInstance;
    page.uf.set('AC');
    fixture.detectChanges();
    const el = fixture.nativeElement as HTMLElement;
    expect(page.resolved('ICMS', 2022)).toEqual(jasmine.objectContaining({ rate: 17, status: 'VALIDADO' }));
    expect(page.resolved('ICMS', 2024)).toEqual(jasmine.objectContaining({ rate: 19, status: 'VALIDADO' }));
    expect(page.resolved('ITCD', 2024)).toEqual(jasmine.objectContaining({ rate: 6, status: 'PENDENTE' }));
    const rows = page.rows();
    expect(rows.map((row) => page.amountOf(row, 'ICMS'))).toEqual([170, null, 190]);
    const text = el.textContent as string;
    expect(text).toContain('Alíquota 19% · Validado');
    expect(text).toContain('Alíquota 6% · Pendente de validação jurídica');
    expect(text).toContain('exceções por mercadoria e operação não estão modeladas');
    http.verify();
  });

  it('leaves the 2023 Acre tax empty because the validated rate changed on April first', () => {
    const acItems = [2023].map((ano) => ({
      ano, uf: 'AC', operacao: 'Vendas', quantidade: 10, valorEstimado: '1000.00',
    }));
    const fixture = TestBed.createComponent(SimuladorPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne((req) => req.params.get('level') === 'SERIE').flush(view(acItems, true, [2023]));
    flushRates(http);
    const page = fixture.componentInstance;
    page.uf.set('AC');
    page.valueInput.set(2000);
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
    http.expectOne((req) => req.params.get('level') === 'SERIE').flush(view(ITEMS));
    flushRates(http, 'error');
    const page = fixture.componentInstance;
    page.uf.set('AC');
    fixture.detectChanges();
    expect(page.ratesFallback()).toBeTrue();
    expect(page.resolved('ICMS', 2024)).toEqual(jasmine.objectContaining({ rate: 19, status: 'PENDENTE' }));
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('A tabela de alíquotas não pôde ser lida');
    http.verify();
  });

  it('shows an alert when the read fails but keeps the fields', () => {
    const fixture = TestBed.createComponent(SimuladorPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne((req) => req.params.get('level') === 'SERIE').flush('x', { status: 500, statusText: 'err' });
    flushRates(http);
    fixture.detectChanges();
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelector('[role="alert"]')?.textContent).toContain('não puderam ser lidos');
    expect(el.querySelector('input[name="qtd"]')).toBeTruthy();
    http.verify();
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
    http.expectOne((req) => req.params.get('level') === 'SERIE').flush(view(ITEMS));
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
