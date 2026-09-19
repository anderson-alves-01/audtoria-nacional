import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { GatesPageComponent } from './gates-page.component';

describe('GatesPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GatesPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('shows G0 and G1 as blocked and never offers approval', () => {
    const fixture = TestBed.createComponent(GatesPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/program-gates').flush({
      canApprove: false,
      humanApprovalFabricated: false,
      flags: { cloud_apply: false },
      gates: [
        {
          id: 'G0',
          component: 'municipal_program',
          status: 'BLOCKED',
          checklist: [{ id: 'sponsor', label: 'Patrocinador nomeado', met: false }],
        },
        {
          id: 'G1',
          component: 'diagnosis',
          status: 'BLOCKED',
          checklist: [{ id: 'dpa', label: 'Diagnóstico LGPD homologado', met: false }],
        },
      ],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('G0');
    expect(text).toContain('BLOCKED');
    expect(text).toContain('não atendido');
    expect(text).toContain('Pode aprovar daqui: não');
    expect(text).not.toContain('Pode aprovar daqui: sim');
    expect(fixture.nativeElement.querySelector('button')).toBeNull();
    http.verify();
  });
});
