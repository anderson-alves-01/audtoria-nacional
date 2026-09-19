import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActiveDebtPageComponent } from './active-debt-page.component';

describe('ActiveDebtPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ActiveDebtPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty official active-debt panel with inscription disabled', () => {
    const fixture = TestBed.createComponent(ActiveDebtPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/active-debt').flush({
      version: 'active-debt-panel-technical-v1',
      commandsDisabled: true,
      inscriptionEnabled: false,
      createsTaxCredit: false,
      credentialStatus: 'CREDENTIAL_REQUIRED',
      g0Status: 'BLOCKED',
      items: [],
      queue: [],
      disclaimer: 'Painel técnico de dívida ativa vazio.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Dívida ativa (painel oficial)');
    expect(text).toContain('CREDENTIAL_REQUIRED');
    expect(text).toContain('G0: BLOCKED');
    expect(text).toContain('Inscrição desativada');
    http.verify();
  });

  it('shows error when active-debt panel API fails', () => {
    const fixture = TestBed.createComponent(ActiveDebtPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/active-debt').flush(
      { title: 'Error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar o painel de dívida ativa',
    );
    http.verify();
  });
});
