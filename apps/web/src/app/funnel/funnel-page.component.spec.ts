import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { FunnelPageComponent } from './funnel-page.component';

describe('FunnelPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FunnelPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders official gold without claiming tax credits or regional money', () => {
    const fixture = TestBed.createComponent(FunnelPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/indicators/official-gold').flush({
      published: true,
      banner: 'DADOS DE FONTE OFICIAL — PROCESSAMENTO TÉCNICO CONCLUÍDO — HOMOLOGAÇÃO HUMANA PENDENTE',
      items: [
        {
          sourceId: 'IBGE-SIDRA',
          indicator: 'ibge_population_estimated',
          maintainer: 'IBGE',
          dataset: 'SIDRA-6579',
          competence: '2026',
          lastExtractedAt: '2026-09-18T00:00:00+00:00',
          formula: 'SIDRA 6579 variável 9324',
          methodologyVersion: 'official-sidra-6579-v1',
          coverageCount: 2,
          qualityLevel: 'TECHNICALLY_VALIDATED',
          homologationStatus: 'REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION',
          officialUrl: 'https://sidra.ibge.gov.br/tabela/6579',
          quarantinedCount: 1,
          numericTotal: 18642470,
        },
      ],
      emptySources: [],
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('ibge_population_estimated');
    expect(fixture.nativeElement.textContent).toContain('HOMOLOGAÇÃO HUMANA PENDENTE');
    expect(fixture.nativeElement.textContent).not.toContain('R$');
    http.verify();
  });

  it('shows empty state when no official gold is published', () => {
    const fixture = TestBed.createComponent(FunnelPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/indicators/official-gold').flush({
      published: false,
      banner: 'DADOS DE FONTE OFICIAL — PROCESSAMENTO TÉCNICO CONCLUÍDO — HOMOLOGAÇÃO HUMANA PENDENTE',
      items: [],
      emptySources: [{ sourceId: 'ESTADO-ICMS-QUOTA', emptyReason: 'Estado piloto não selecionado' }],
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Nenhum Gold oficial publicado');
    expect(fixture.nativeElement.textContent).toContain('ESTADO-ICMS-QUOTA');
    http.verify();
  });
});
