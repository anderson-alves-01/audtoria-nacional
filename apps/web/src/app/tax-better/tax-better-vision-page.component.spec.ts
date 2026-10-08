import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { TaxBetterVisionPageComponent } from './tax-better-vision-page.component';

describe('TaxBetterVisionPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaxBetterVisionPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
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
    expect(text).toContain('cidade: Brasília');
    expect(text).toContain('150,00');
    expect(text).toContain('—');
    expect(text).toContain('sem aprovação');
    expect(text).toContain('Cria crédito: não');
    http.verify();
  });
});
