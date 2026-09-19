import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { OpsGovernancePageComponent } from './ops-governance-page.component';

describe('OpsGovernancePageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OpsGovernancePageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders local ops governance with G10 blocked', () => {
    const fixture = TestBed.createComponent(OpsGovernancePageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/ops-governance').flush({
      version: 'ops-governance-technical-v1',
      canDeploy: false,
      canApprove: false,
      g10Status: 'BLOCKED',
      runbooksComplete: true,
      runbooks: [
        {
          id: 'incident_response',
          label: 'Resposta a incidentes locais',
          path: 'docs/operations/incident-response-local.md',
          present: true,
        },
      ],
      disclaimer: 'Governança operacional técnica local.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Operação e governança local');
    expect(text).toContain('BLOCKED');
    expect(text).toContain('Deploy autorizado: não');
    expect(text).toContain('incident-response-local.md');
    http.verify();
  });

  it('shows error when ops governance API fails', () => {
    const fixture = TestBed.createComponent(OpsGovernancePageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/ops-governance').flush(
      { title: 'Error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar a governança operacional',
    );
    http.verify();
  });
});
