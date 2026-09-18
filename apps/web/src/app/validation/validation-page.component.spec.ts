import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ValidationPageComponent } from './validation-page.component';

describe('ValidationPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ValidationPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('keeps an idle empty instruction before submit', () => {
    const fixture = TestBed.createComponent(ValidationPageComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Preencha o crédito identificado');
  });

  it('shows validated status after a successful API response', () => {
    const fixture = TestBed.createComponent(ValidationPageComponent);
    const page = fixture.componentInstance;
    const http = TestBed.inject(HttpTestingController);
    page.creditId = '11111111-1111-4111-8111-111111111051';
    page.evidenceId = '11111111-1111-4111-8111-111111111071';
    page.territoryId = '11111111-1111-4111-8111-111111111021';
    page.purposeId = '11111111-1111-4111-8111-111111111041';
    page.accessToken = 'synthetic-token';
    page.rationale = 'Synthetic local approval rationale.';
    page.items.forEach((item) => (item.satisfied = true));
    page.submit();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Enviando decisão');
    http.expectOne('/v1/tax-credits/11111111-1111-4111-8111-111111111051/validations').flush({
      validationStatus: 'VALIDATED',
      collectionStatus: 'NOT_STARTED',
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('VALIDATED');
    http.verify();
  });

  it('shows an unchanged-credit message on conflict', () => {
    const fixture = TestBed.createComponent(ValidationPageComponent);
    const page = fixture.componentInstance;
    const http = TestBed.inject(HttpTestingController);
    page.creditId = '11111111-1111-4111-8111-111111111051';
    page.evidenceId = '11111111-1111-4111-8111-111111111071';
    page.submit();
    http.expectOne('/v1/tax-credits/11111111-1111-4111-8111-111111111051/validations').flush(
      { title: 'Conflict' },
      { status: 409, statusText: 'Conflict' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('O crédito não foi alterado');
    http.verify();
  });

  it('shows forbidden when the API returns 403', () => {
    const fixture = TestBed.createComponent(ValidationPageComponent);
    const page = fixture.componentInstance;
    const http = TestBed.inject(HttpTestingController);
    page.creditId = '11111111-1111-4111-8111-111111111051';
    page.evidenceId = '11111111-1111-4111-8111-111111111071';
    page.submit();
    http.expectOne('/v1/tax-credits/11111111-1111-4111-8111-111111111051/validations').flush(
      { title: 'Forbidden' },
      { status: 403, statusText: 'Forbidden' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('A API recusou a validação');
    http.verify();
  });
});
