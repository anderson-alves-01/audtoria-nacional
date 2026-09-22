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

  it('renders a non-binding catalog with preserved document lineage', () => {
    const fixture = TestBed.createComponent(CalendarPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/regulatory/ibs-cbs').flush({
      binding: false,
      operational: false,
      homologated: false,
      disclaimer: 'Non-binding catalog linked to preserved official documents.',
      catalogVersion: 'catalog-official-docs-v1',
      preservedDocuments: [
        {
          sourceId: 'PLANALTO-LC-214',
          published: true,
          methodologyVersion: 'official-planalto-lc214-v1',
          officialUrl: 'https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm',
          bronzeSha256: 'abc',
          checksumSha256: 'def',
          landingManifestPath: 'landing/planalto-lc214.json',
          binding: false,
          operational: false,
          homologated: false,
        },
      ],
      items: [
        {
          code: 'LC-214-2025',
          title: 'LC 214/2025 — IBS/CBS (documento oficial preservável)',
          source: 'https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm',
          kind: 'NORM',
          status: 'NON_BINDING',
          binding: false,
          notes: 'binding=false.',
        },
      ],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('não vinculante');
    expect(text).toContain('catalog-official-docs-v1');
    expect(text).toContain('PLANALTO-LC-214');
    expect(text).toContain('SHA-256 def');
    expect(text).toContain('Operacional: não');
    expect(text).toContain('Homologado: não');
    expect(text).not.toContain('Homologado: sim');
    http.verify();
  });
});
