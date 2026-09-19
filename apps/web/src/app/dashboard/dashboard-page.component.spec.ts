import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { DashboardPageComponent } from './dashboard-page.component';

describe('DashboardPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: ActivatedRoute, useValue: { snapshot: { data: { dashboardId: 'transferencias' } } } },
      ],
    }).compileComponents();
  });

  it('shows empty official state without synthetic values', () => {
    const fixture = TestBed.createComponent(DashboardPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/dashboards/transferencias').flush({
      title: 'Transferências',
      banner: 'DADOS DE FONTE OFICIAL — PROCESSAMENTO TÉCNICO CONCLUÍDO — HOMOLOGAÇÃO HUMANA PENDENTE',
      emptyReason: 'Somente valores oficiais publicados. Dicionário FPM não é valor transferido.',
      published: false,
      commandsDisabled: true,
      homologationStatus: 'REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION',
      items: [],
      emptySources: [
        {
          sourceId: 'TESOURO-FPM-VALORES',
          emptyReason: 'Sem Gold oficial publicado para TESOURO-FPM-VALORES.',
          status: 'EMPTY',
        },
      ],
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Dicionário FPM não é valor transferido');
    expect(fixture.nativeElement.textContent).toContain('TESOURO-FPM-VALORES');
    expect(fixture.nativeElement.textContent).toContain('Homologação');
    expect(fixture.nativeElement.textContent).toContain('Comandos de cobrança');
    expect(fixture.nativeElement.textContent).not.toContain('R$');
    http.verify();
  });

  it('shows lineage when official gold is published', () => {
    const fixture = TestBed.createComponent(DashboardPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/dashboards/transferencias').flush({
      title: 'Transferências',
      banner: 'DADOS DE FONTE OFICIAL — PROCESSAMENTO TÉCNICO CONCLUÍDO — HOMOLOGAÇÃO HUMANA PENDENTE',
      emptyReason: 'Somente valores oficiais publicados.',
      published: true,
      commandsDisabled: true,
      homologationStatus: 'REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION',
      emptySources: [],
      items: [
        {
          sourceId: 'TESOURO-TRANSPARENTE',
          indicator: 'tesouro_constitutional_transfer_types',
          maintainer: 'Tesouro Nacional',
          dataset: 'TESOURO-TRANSFERENCIAS-DICIONARIO',
          competence: '2026',
          formula: 'Lista publicada.',
          methodologyVersion: 'official-tesouro-transfer-types-v1',
          coverageCount: 1,
          qualityLevel: 'TECHNICALLY_VALIDATED',
          homologationStatus: 'REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION',
          officialUrl: 'https://www.tesourotransparente.gov.br/',
          quarantinedCount: 0,
          numericTotal: null,
          valueKind: 'CATALOG_METADATA',
          financial: false,
          lineageLineCount: 1,
          lineage: {
            bronzeSha256: 'abc',
            landingManifestPath: 'landing/manifest.json',
            endpoint: 'https://example.invalid/transferencias',
          },
        },
      ],
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Lineage');
    expect(fixture.nativeElement.textContent).toContain('landing/manifest.json');
    expect(fixture.nativeElement.textContent).toContain('linhas 1');
    http.verify();
  });
});
