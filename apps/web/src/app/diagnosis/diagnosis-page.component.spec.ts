import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { DiagnosisPageComponent } from './diagnosis-page.component';

describe('DiagnosisPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DiagnosisPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty technical diagnosis without recovery meta', () => {
    const fixture = TestBed.createComponent(DiagnosisPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/diagnosis').flush({
      version: 'diagnosis-technical-v1',
      binding: false,
      operational: false,
      homologated: false,
      commandsDisabled: true,
      recoveryMeta: null,
      g1Status: 'BLOCKED',
      checklist: [
        { id: 'sponsor_governance', label: 'Patrocinador e grupo gestor definidos', met: false },
      ],
      items: [],
      disclaimer: 'Diagnóstico técnico vazio. Sem meta de recuperação.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Diagnóstico municipal técnico');
    expect(text).toContain('G1: BLOCKED');
    expect(text).toContain('Meta de recuperação: ausente');
    expect(text).toContain('pendente');
    expect(text).not.toContain('recuperação prometida');
    http.verify();
  });
});
