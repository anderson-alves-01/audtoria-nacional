import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { AuditRulesPageComponent } from './audit-rules-page.component';

describe('AuditRulesPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AuditRulesPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders non-binding rules and never claims tax credit', () => {
    const fixture = TestBed.createComponent(AuditRulesPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/audit-rules').flush({
      catalogVersion: 'audit-rules-synthetic-v1',
      binding: false,
      operational: false,
      homologated: false,
      commandsDisabled: true,
      createsTaxCredit: false,
      taxPotentialAsCredit: false,
      disclaimer: 'Catálogo técnico de regras não vinculantes.',
      items: [
        {
          code: 'ISS-CADASTRO-CROSSCHECK-PLACEHOLDER',
          title: 'Cruzamento cadastral ISS — placeholder não executável',
          domain: 'iss',
          status: 'NON_BINDING',
          binding: false,
          notes: 'Regra técnica vazia.',
        },
      ],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('não vinculantes');
    expect(text).toContain('Cria crédito: não');
    expect(text).toContain('NON_BINDING');
    expect(text).not.toContain('Cria crédito: sim');
    http.verify();
  });
});
