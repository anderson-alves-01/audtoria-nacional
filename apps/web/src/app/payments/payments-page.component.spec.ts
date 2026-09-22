import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { PaymentsPageComponent } from './payments-page.component';

describe('PaymentsPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PaymentsPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty official payments panel with commands disabled', () => {
    const fixture = TestBed.createComponent(PaymentsPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/payments').flush({
      version: 'payments-panel-technical-v1',
      commandsDisabled: true,
      recoveryInvented: false,
      createsTaxCredit: false,
      credentialStatus: 'CREDENTIAL_REQUIRED',
      g6Status: 'LOCAL_GO_OFFICIAL_BLOCKED',
      items: [],
      installments: [],
      disclaimer: 'Painel técnico de pagamentos e parcelamentos vazio.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Pagamentos e parcelamentos (painel oficial)');
    expect(text).toContain('CREDENTIAL_REQUIRED');
    expect(text).toContain('LOCAL_GO_OFFICIAL_BLOCKED');
    expect(text).toContain('Sem baixa ou adesão');
    http.verify();
  });

  it('shows error when payments panel API fails', () => {
    const fixture = TestBed.createComponent(PaymentsPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/payments').flush(
      { title: 'Error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar o painel de pagamentos',
    );
    http.verify();
  });
});
