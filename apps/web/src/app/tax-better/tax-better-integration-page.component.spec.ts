import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { TaxBetterIntegrationPageComponent } from './tax-better-integration-page.component';

describe('TaxBetterIntegrationPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaxBetterIntegrationPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('saves the field map and does not offer a malha export', () => {
    const fixture = TestBed.createComponent(TaxBetterIntegrationPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/data-sources/TAX-BETTER-ENTRADA/tax-better-config').flush({
      channel: 'api',
      fieldMap: {
        organ: 'orgao',
        tax: 'imposto',
        fgo: 'fgo',
        operationValue: 'op_valor',
        operationBase: 'op_base',
        operationTax: 'op_imposto',
        malhaValue: 'malha_valor',
        malhaBase: 'malha_base',
        malhaTax: 'malha_imposto',
      },
      endpoint: 'https://example.invalid',
      secretName: 'DETRAN_API_KEY',
      createsTaxCredit: false,
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Sem aprovação, não há exportação');
    expect(text).not.toContain('Enviar notificação');
    const save = Array.from(fixture.nativeElement.querySelectorAll('button')).find((node) =>
      (node as HTMLButtonElement).textContent?.includes('Gravar mapa'),
    ) as HTMLButtonElement;
    save.click();
    const saved = http.expectOne('/v1/data-sources/TAX-BETTER-ENTRADA/tax-better-config');
    expect(saved.request.method).toBe('PUT');
    expect(saved.request.body.secretName).toBe('DETRAN_API_KEY');
    expect(saved.request.body.secret).toBeUndefined();
    expect(saved.request.body.secretValue).toBeUndefined();
    saved.flush({
      channel: 'api',
      fieldMap: saved.request.body.fieldMap,
      endpoint: 'https://example.invalid',
      secretName: 'DETRAN_API_KEY',
      createsTaxCredit: false,
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Nenhum crédito foi criado');
    http.verify();
  });
});
