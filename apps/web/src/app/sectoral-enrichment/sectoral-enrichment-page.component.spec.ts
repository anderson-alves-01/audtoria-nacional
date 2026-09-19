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

  it('renders sectoral shell with ANP, ANEEL, BCB, EPE and Anatel partial activation without tax credit', () => {
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
        {
          sourceId: 'ANEEL-DADOS-ABERTOS',
          maintainer: 'ANEEL',
          status: 'TECHNICALLY_APPROVED',
          ingestAllowed: true,
          structuredOfficialSource: 'ckan_datastore_indqual_municipio',
        },
        {
          sourceId: 'BCB-SGS-OLINDA',
          maintainer: 'Banco Central',
          status: 'TECHNICALLY_APPROVED',
          ingestAllowed: true,
          structuredOfficialSource: 'sgs_json_allowlist',
        },
        {
          sourceId: 'EPE-DADOS-ABERTOS',
          maintainer: 'EPE',
          status: 'TECHNICALLY_APPROVED',
          ingestAllowed: true,
          structuredOfficialSource: 'anuario_dados_brutos_xlsx',
        },
        {
          sourceId: 'ANATEL-DADOS-ABERTOS',
          maintainer: 'Anatel',
          status: 'TECHNICALLY_APPROVED',
          ingestAllowed: true,
          structuredOfficialSource: 'meu_municipio_zip_csv_ibge7',
        },
      ],
      items: [],
      disclaimer: 'ANP, ANEEL, BCB, EPE e Anatel ativadas; CNES bloqueada.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Enriquecimento setorial');
    expect(text).toContain('Ingestão habilitada: sim');
    expect(text).toContain('Cria crédito: não');
    expect(text).toContain('ANP-REVENDEDORES');
    expect(text).toContain('ANEEL-DADOS-ABERTOS');
    expect(text).toContain('BCB-SGS-OLINDA');
    expect(text).toContain('EPE-DADOS-ABERTOS');
    expect(text).toContain('ANATEL-DADOS-ABERTOS');
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
