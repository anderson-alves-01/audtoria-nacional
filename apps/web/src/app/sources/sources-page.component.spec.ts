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
          status: 'TECHNICALLY_APPROVED',
          ingestAllowed: true,
          createsTaxCredit: false,
        },
      ],
    });
    fixture.detectChanges();
    http.expectOne('/v1/indicators/source-enrichment?sourceId=IBGE-SIDRA').flush({
      sourceId: 'IBGE-SIDRA',
      sourceRole: 'REFERENCE_ENRICHMENT',
      published: false,
      indicatorCount: 0,
      createsTaxCredit: false,
      emptyReason: 'Nenhum Gold oficial publicado',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('IBGE-SIDRA');
    expect(text).toContain('Cria crédito: não');
    expect(text).not.toContain('Cria crédito: sim');
    expect(text).toContain('HOMOLOGAÇÃO HUMANA PENDENTE');
    http.verify();
  });

  it('ingests the official source and shows enrichment without creating tax credits', () => {
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
          status: 'TECHNICALLY_APPROVED',
          ingestAllowed: true,
          createsTaxCredit: false,
        },
      ],
    });
    fixture.detectChanges();
    http.expectOne('/v1/indicators/source-enrichment?sourceId=IBGE-SIDRA').flush({
      sourceId: 'IBGE-SIDRA',
      published: false,
      indicatorCount: 0,
      createsTaxCredit: false,
    });
    fixture.detectChanges();
    const button = fixture.nativeElement.querySelector('button') as HTMLButtonElement;
    expect(button.textContent).toContain('Ingerir fonte oficial');
    button.click();
    http.expectOne('/v1/data-sources/IBGE-SIDRA/ingest').flush({
      sourceId: 'IBGE-SIDRA',
      taxCreditCreated: false,
      receivedCount: 3,
      silverCount: 2,
      quarantinedCount: 1,
    });
    fixture.detectChanges();
    http.expectOne('/v1/indicators/source-enrichment?sourceId=IBGE-SIDRA').flush({
      sourceId: 'IBGE-SIDRA',
      sourceRole: 'REFERENCE_ENRICHMENT',
      published: true,
      indicatorCount: 2,
      createsTaxCredit: false,
      banner: 'DADOS DE FONTE OFICIAL — PROCESSAMENTO TÉCNICO CONCLUÍDO — HOMOLOGAÇÃO HUMANA PENDENTE',
      homologationStatus: 'REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION',
      formula: 'SIDRA 6579',
      methodologyVersion: 'official-sidra-6579-v1',
      competence: '2026',
      qualityLevel: 'TECHNICALLY_VALIDATED',
      quarantinedCount: 1,
      officialUrl: 'https://sidra.ibge.gov.br/tabela/6579',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Indicadores: 2');
    expect(text).toContain('Nenhum crédito tributário foi criado');
    expect(text).not.toContain('Cria crédito: sim');
    http.verify();
  });
});
