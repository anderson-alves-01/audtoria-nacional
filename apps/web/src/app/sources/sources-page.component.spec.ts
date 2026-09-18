import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { SourcesPageComponent } from './sources-page.component';

describe('SourcesPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SourcesPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('shows catalog items and never claims tax-credit creation', () => {
    const fixture = TestBed.createComponent(SourcesPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/data-sources').flush({
      items: [
        {
          sourceId: 'IBGE-SIDRA',
          name: 'IBGE/SIDRA',
          sourceRole: 'REFERENCE_ENRICHMENT',
          accessClassification: 'PUBLIC_OPEN',
          status: 'APPROVED',
          ingestAllowed: true,
          createsTaxCredit: false,
        },
      ],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('IBGE-SIDRA');
    expect(text).toContain('Cria crédito: não');
    expect(text).not.toContain('Cria crédito: sim');
    http.verify();
  });
});
