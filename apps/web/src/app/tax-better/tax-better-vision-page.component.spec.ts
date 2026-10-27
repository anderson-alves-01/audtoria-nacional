import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { TaxBetterVisionPageComponent } from './tax-better-vision-page.component';

describe('TaxBetterVisionPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaxBetterVisionPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();
  });

  it('shows the empty reason and never claims a tax credit', () => {
    const fixture = TestBed.createComponent(TaxBetterVisionPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/tax-better/vision').flush({
      createsTaxCredit: false,
      approvedExport: false,
      emptyReason: 'Ainda não há arquivo autorizado na visão.',
      rows: [],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Ainda não há arquivo autorizado na visão.');
    expect(text).toContain('Cria crédito: não');
    expect(text).not.toContain('4.000.000');
    http.verify();
  });

  it('renders operation and malha and leaves a missing measure blank', () => {
    const fixture = TestBed.createComponent(TaxBetterVisionPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/tax-better/vision').flush({
      createsTaxCredit: false,
      approvedExport: false,
      emptyReason: null,
      rows: [
        {
          imposto: 'ICMS',
          fgo: 'VENDA PJ',
          variables: { cidade: 'Brasília' },
          operacao: { valor: '150', baseCalculo: null, imposto: null },
          malha: { valor: null, baseCalculo: null, imposto: '4' },
          approved: false,
        },
      ],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('ICMS');
    expect(text).toContain('VENDA PJ');
    expect(text).toContain('150,00');
    expect(text).toContain('—');
    const row = fixture.componentInstance.rows()[0];
    const cell = (id: string) => fixture.componentInstance.columns.find((c) => c.id === id)?.value(row);
    expect(cell('variaveis')).toBe('cidade: Brasília');
    expect(cell('aprovacao')).toBe('sem aprovação');
    expect(cell('ml_valor')).toBeNull();
    expect(fixture.componentInstance.sumMalha()).toBeNull();
    expect(text).toContain('Cria crédito: não');
    http.verify();
  });

  it('filters the malha reading by tax', () => {
    const fixture = TestBed.createComponent(TaxBetterVisionPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/tax-better/vision').flush({
      createsTaxCredit: false,
      approvedExport: false,
      emptyReason: null,
      rows: [
        {
          orgao: 'DETRAN',
          imposto: 'ICMS',
          fgo: 'VENDA PJ',
          periodo: '2026-01',
          variables: { cidade: 'Brasília' },
          operacao: { valor: '150', baseCalculo: null, imposto: null },
          malha: { valor: '10', baseCalculo: null, imposto: null },
          approved: false,
        },
        {
          orgao: 'OUTRO',
          imposto: 'ISS',
          fgo: 'FORA DF',
          periodo: '2026-02',
          variables: { cidade: 'Taguatinga' },
          operacao: { valor: '20', baseCalculo: null, imposto: null },
          malha: { valor: null, baseCalculo: null, imposto: null },
          approved: false,
        },
      ],
    });
    fixture.detectChanges();
    fixture.componentInstance.choose('imposto', 'ISS');
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('ISS');
    expect(fixture.componentInstance.rows().map((r) => r.variables['cidade'])).toEqual(['Taguatinga']);
    expect(fixture.componentInstance.sumOperation()).toBe(20);
    expect(fixture.componentInstance.sumMalha()).toBeNull();
    expect(text).toContain('Prontas para a malha');
    expect(text).toContain('Sem aprovação, nada é exportado');
    http.verify();
  });

  it('cross-filters, drills down and compares periods without turning a missing side into zero', () => {
    const fixture = TestBed.createComponent(TaxBetterVisionPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    const side = (valor: string | null) => ({ valor, baseCalculo: null, imposto: null });
    http.expectOne('/v1/tax-better/vision').flush({
      createsTaxCredit: false,
      approvedExport: false,
      emptyReason: null,
      rows: [
        { orgao: 'A', imposto: 'ICMS', fgo: 'F1', periodo: '2026-01', variables: {}, operacao: side('100'), malha: side(null), approved: false },
        { orgao: 'A', imposto: 'ICMS', fgo: 'F1', periodo: '2026-02', variables: {}, operacao: side('150'), malha: side(null), approved: false },
        { orgao: 'B', imposto: 'ISS', fgo: 'F2', periodo: '2026-02', variables: {}, operacao: side('30'), malha: side(null), approved: false },
        { orgao: 'B', imposto: 'ISS', fgo: 'F2', periodo: '2026-01', variables: {}, operacao: side(null), malha: side(null), approved: false },
      ],
    });
    fixture.detectChanges();
    const page = fixture.componentInstance;

    page.onPick({ value: 'ICMS', multi: false }, 'imposto');
    expect(page.rows().length).toBe(2);
    expect(page.sumOperation()).toBe(250);
    // o grafico principal continua mostrando as demais categorias, esmaecidas
    expect(page.mainChart().categories).toEqual(['ICMS', 'ISS']);

    page.filters.clear();
    page.drill('ISS');
    expect(page.mainDimension()).toBe('fgo');
    expect(page.rows().length).toBe(2);

    page.filters.clear();
    page.choose('periodo', '2026-01');
    page.compareWith.set('2026-02');
    const comparison = page.comparison();
    const iss = comparison?.rows.find((line) => line.category === 'ISS');
    expect(iss?.current).toBeNull();
    expect(iss?.delta).toBeNull();
    const icms = comparison?.rows.find((line) => line.category === 'ICMS');
    expect(icms?.delta).toBe(-50);
    http.verify();
  });
});