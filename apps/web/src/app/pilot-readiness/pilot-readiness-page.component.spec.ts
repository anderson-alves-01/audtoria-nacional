import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { PilotReadinessPageComponent } from './pilot-readiness-page.component';

describe('PilotReadinessPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PilotReadinessPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders technical pilot readiness with G9 blocked', () => {
    const fixture = TestBed.createComponent(PilotReadinessPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/pilot-readiness').flush({
      version: 'pilot-readiness-technical-v1',
      technicalReady: true,
      institutionalReady: false,
      pilotMunicipalityApproved: false,
      g9Status: 'BLOCKED',
      checklist: [
        {
          id: 'ci_reproducible',
          label: 'CI Python/web/containers reproduzível',
          met: true,
          category: 'technical',
        },
        {
          id: 'pilot_municipality',
          label: 'Município piloto formalmente aprovado',
          met: false,
          category: 'institutional',
        },
      ],
      disclaimer: 'Checklist técnico de prontidão para piloto assistido.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Prontidão técnica para piloto');
    expect(text).toContain('BLOCKED');
    expect(text).toContain('Institucional: pendente');
    expect(text).toContain('Município piloto formalmente aprovado');
    http.verify();
  });

  it('shows error when pilot readiness API fails', () => {
    const fixture = TestBed.createComponent(PilotReadinessPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/pilot-readiness').flush(
      { title: 'Error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar a prontidão de piloto',
    );
    http.verify();
  });
});
