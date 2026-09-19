import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { SectoralEnrichmentPageComponent } from './sectoral-enrichment-page.component';

describe('SectoralEnrichmentPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SectoralEnrichmentPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders sectoral shell with ANP partial activation without tax credit', () => {
    const fixture = TestBed.createComponent(SectoralEnrichmentPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/sectoral-enrichment').flush({
      version: 'sectoral-enrichment-technical-v1',
      ingestEnabled: true,
      createsTaxCredit: false,
      institutionalStatus: 'PARTIAL_TECHNICAL_ACTIVATION',
      sources: [
        {
          sourceId: 'ANP-REVENDEDORES',
          maintainer: 'ANP',
          status: 'TECHNICALLY_APPROVED',
          ingestAllowed: true,
          structuredOfficialSource: 'rest_api_verified',
        },
      ],
      items: [],
      disclaimer: 'ANP ativada com escopo UF; demais bloqueadas.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Enriquecimento setorial');
    expect(text).toContain('Ingestão habilitada: sim');
    expect(text).toContain('Cria crédito: não');
    expect(text).toContain('ANP-REVENDEDORES');
    expect(text).toContain('TECHNICALLY_APPROVED');
    http.verify();
  });

  it('shows error when sectoral enrichment API fails', () => {
    const fixture = TestBed.createComponent(SectoralEnrichmentPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/sectoral-enrichment').flush(
      { title: 'Error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar o enriquecimento setorial',
    );
    http.verify();
  });
});
