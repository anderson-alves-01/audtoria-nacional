import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
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

function view(items: unknown[], withRun = true): Record<string, unknown> {
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
    years: [2021, 2022],
    operations: OPERATIONS,
    ufs: ['AC', 'SP'],
    run: withRun ? run : null,
    items,
  };
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

  it('shows an empty state and the simulation banner when nothing was loaded', () => {
    const { el, http } = loaded([], false);
    expect(el.textContent).toContain('Simulação · não é apuração fiscal');
    expect(el.textContent).toContain('Nenhuma carga validada do SPED');
    expect(el.querySelector('form[aria-label="Escolhas do simulador"]')).toBeNull();
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
    const municipality = el.querySelector('select[name="municipio"]') as HTMLSelectElement;
    expect(municipality.disabled).toBeTrue();
    http.verify();
  });

  it('shows value, quantity, operation and tax for one operation without mixing others', () => {
    const { fixture, page, el, http } = loaded();
    page.uf.set('SP');
    fixture.detectChanges();
    const text = el.textContent as string;
    expect(text).toContain('Parte A');
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

  it('shows an alert when the read fails', () => {
    const fixture = TestBed.createComponent(SimuladorPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne((req) => req.params.get('level') === 'SERIE').flush('x', { status: 500, statusText: 'err' });
    fixture.detectChanges();
    expect((fixture.nativeElement as HTMLElement).querySelector('[role="alert"]')?.textContent).toContain('não puderam ser lidos');
    http.verify();
  });
});
