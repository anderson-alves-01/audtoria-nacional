import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { SpedOperacoesPageComponent } from './sped-operacoes-page.component';

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
  runId: '0b7a8d0e-0000-4000-8000-000000000001',
  checksum: 'ab'.repeat(32),
  layoutVersion: 'sped-nfe-uf-cfop-v1',
  competence: '2021-25',
  loadedAt: '2026-10-27T12:00:00+00:00',
  receivedCount: 3,
};

function view(items: unknown[], withRun = true, level = 'SERIE'): Record<string, unknown> {
  return {
    sourceId: 'SPED-NFE-UF-CFOP',
    valueKind: 'ESTIMATED_ALLOCATION',
    banner: 'Base exploratória, não homologada. O valor por UF é rateio estimado.',
    formula: 'Valor nacional do CFOP × participação da UF',
    homologated: false,
    published: false,
    createsTaxCredit: false,
    level,
    page: 1,
    pageSize: 1000,
    total: items.length,
    years: [2021, 2022, 2023, 2024, 2025],
    operations: OPERATIONS,
    ufs: ['AC', 'SP'],
    run: withRun ? run : null,
    items,
  };
}

describe('SpedOperacoesPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SpedOperacoesPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();
  });

  it('keeps the exploratory banner and shows an empty state when nothing was loaded', () => {
    const fixture = TestBed.createComponent(SpedOperacoesPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne((req) => req.url === '/v1/sped-operacoes' && req.params.get('level') === 'SERIE').flush(view([], false));
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Exploratório · não homologado');
    expect(text).toContain('Nenhuma carga validada do SPED');
    expect(text).not.toContain('Quantidade observada');
    http.verify();
  });

  it('separates observed quantity from estimated value and never sums operations', () => {
    const fixture = TestBed.createComponent(SpedOperacoesPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http
      .expectOne((req) => req.params.get('level') === 'SERIE')
      .flush(
        view([
          { ano: 2021, uf: 'SP', operacao: 'Vendas', quantidade: 1200, valorEstimado: '5000.00' },
          { ano: 2021, uf: 'SP', operacao: 'Compras', quantidade: 800, valorEstimado: '9000.00' },
          { ano: 2021, uf: 'AC', operacao: 'Vendas', quantidade: 0, valorEstimado: null },
        ]),
      );
    fixture.detectChanges();
    http.expectOne((req) => req.params.get('level') === 'CFOP').flush(
      view(
        [{ ano: 2021, uf: 'SP', operacao: 'Vendas', cfop: '5102', quantidade: 1200, valorEstimado: '5000.00' }],
        true,
        'CFOP',
      ),
    );
    fixture.detectChanges();
    const el = fixture.nativeElement as HTMLElement;
    const text = el.textContent as string;
    expect(text).toContain('Quantidade por UF');
    expect(text).toContain('Valor estimado por UF');
    expect(text).toContain('Valor estimado (rateio)');
    expect(text).toContain('Sem total entre operações');
    expect(text).toContain('Cria crédito: não');
    // Vendas only: 1.200 observed, never 2.000 (Vendas + Compras).
    expect(text).toContain('1.200');
    expect(text).not.toContain('2.000');
    expect(el.querySelectorAll('app-sped-hex-map').length).toBe(2);
    expect(el.querySelectorAll('app-sped-hex-map g.cell').length).toBe(54);
    // UF with no value stays an empty hexagon, not a zero-coloured one.
    expect(el.querySelectorAll('app-sped-hex-map g.cell.empty').length).toBeGreaterThan(0);
    http.verify();
  });

  it('shows the lineage of the load and the table with UF by CFOP', () => {
    const fixture = TestBed.createComponent(SpedOperacoesPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne((req) => req.params.get('level') === 'SERIE').flush(view([]));
    fixture.detectChanges();
    http.expectOne((req) => req.params.get('level') === 'CFOP').flush(view([], true, 'CFOP'));
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain(run.runId);
    expect(text).toContain(run.checksum);
    expect(text).toContain('sped-nfe-uf-cfop-v1');
    expect(text).toContain('UF × CFOP');
    http.verify();
  });

  it('shows an alert when the read fails', () => {
    const fixture = TestBed.createComponent(SpedOperacoesPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne((req) => req.params.get('level') === 'SERIE').flush('x', { status: 500, statusText: 'err' });
    fixture.detectChanges();
    expect((fixture.nativeElement as HTMLElement).querySelector('[role="alert"]')?.textContent).toContain('não puderam ser lidos');
    http.verify();
  });
});
