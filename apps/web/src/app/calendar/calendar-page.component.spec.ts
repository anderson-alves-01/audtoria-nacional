import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { CalendarPageComponent } from './calendar-page.component';

describe('CalendarPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CalendarPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders a non-binding catalog and never claims homologation', () => {
    const fixture = TestBed.createComponent(CalendarPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/regulatory/ibs-cbs').flush({
      binding: false,
      operational: false,
      homologated: false,
      disclaimer: 'Non-binding synthetic catalog.',
      catalogVersion: 'catalog-synthetic-v1',
      items: [
        {
          code: 'SIMULATION-NON-BINDING',
          title: 'Simulação IBS/CBS — não vinculante',
          source: 'synthetic-catalog',
          kind: 'SIMULATION',
          status: 'NON_BINDING',
          binding: false,
          notes: 'Resultados hipotéticos.',
        },
      ],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('não vinculante');
    expect(text).toContain('Non-binding synthetic catalog.');
    expect(text).toContain('Operacional: não');
    expect(text).toContain('Homologado: não');
    expect(text).toContain('NON_BINDING');
    expect(text).not.toContain('Homologado: sim');
    http.verify();
  });
});
