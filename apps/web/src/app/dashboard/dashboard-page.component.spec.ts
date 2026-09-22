import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { PublicOpenSessionService } from '../auth/public-open-session.service';
import { DashboardPageComponent } from './dashboard-page.component';

describe('DashboardPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: { data: of({ dashboardId: 'transferencias' }) },
        },
        {
          provide: PublicOpenSessionService,
          useValue: {
            ensureSession: () => Promise.resolve(),
            authHeaders: () => null,
          },
        },
      ],
    }).compileComponents();
  });

  it('shows empty official state without synthetic values', async () => {
    const fixture = TestBed.createComponent(DashboardPageComponent);
    const httpCtrl = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    await fixture.whenStable();
    httpCtrl.expectOne('/v1/dashboards/transferencias').flush({
      title: 'Transferências',
      banner: 'DADOS DE FONTE OFICIAL — REFERÊNCIA HUMANAMENTE VALIDADA — NÃO É CRÉDITO TRIBUTÁRIO',
      emptyReason: 'Somente valores oficiais publicados. Dicionário FPM não é valor transferido.',
      published: false,
      commandsDisabled: true,
      homologationStatus: 'REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY',
      items: [],
      emptySources: [
        {
          sourceId: 'TESOURO-FPM-VALORES',
          emptyReason: 'Sem Gold oficial publicado para TESOURO-FPM-VALORES.',
          status: 'EMPTY',
        },
      ],
      kpis: [],
      charts: [],
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Dicionário FPM não é valor transferido');
    expect(fixture.nativeElement.textContent).toContain('Tesouro Nacional — FPM publicado');
    expect(fixture.nativeElement.textContent).not.toContain('TESOURO-FPM-VALORES');
    expect(fixture.nativeElement.textContent).not.toContain('REAL_OFFICIAL_DATA');
    expect(fixture.nativeElement.textContent).toContain('Painel aberto');
    expect(fixture.nativeElement.textContent).toContain('Não é crédito tributário');
    expect(fixture.nativeElement.textContent).toContain('Comandos de cobrança');
    expect(fixture.nativeElement.textContent).not.toContain('R$');
    fixture.destroy();
    httpCtrl.verify();
  });

  it('shows lineage when official gold is published', async () => {
    const fixture = TestBed.createComponent(DashboardPageComponent);
    const httpCtrl = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    await fixture.whenStable();
    httpCtrl.expectOne('/v1/dashboards/transferencias').flush({
      title: 'Transferências',
      banner: 'DADOS DE FONTE OFICIAL — REFERÊNCIA HUMANAMENTE VALIDADA — NÃO É CRÉDITO TRIBUTÁRIO',
      emptyReason: 'Somente valores oficiais publicados.',
      published: true,
      commandsDisabled: true,
      homologationStatus: 'REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY',
      emptySources: [],
      kpis: [
        {
          id: 'kpi-1',
          label: 'FPM',
          value: 1000,
          unit: 'BRL',
          valueKind: 'TRANSFER_AMOUNT_AS_PUBLISHED',
          sourceId: 'TESOURO-FPM-VALORES',
          evidenceId: 'g1',
        },
      ],
      charts: [
        {
          id: 'coverage-by-source',
          title: 'Cobertura por fonte oficial',
          type: 'bar',
          unit: 'COUNT',
          valueKind: 'REFERENCE_QUANTITY',
          series: [{ name: 'Cobertura', points: [{ x: 'TESOURO-FPM-VALORES', y: 2 }] }],
          evidenceIds: ['g1'],
        },
      ],
      items: [
        {
          sourceId: 'TESOURO-FPM-VALORES',
          indicator: 'fpm_published',
          maintainer: 'Tesouro Nacional',
          dataset: 'TESOURO-FPM',
          competence: '2026',
          formula: 'Soma publicada.',
          methodologyVersion: 'official-fpm-v1',
          coverageCount: 2,
          qualityLevel: 'TECHNICALLY_VALIDATED',
          homologationStatus: 'REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY',
          officialUrl: 'https://www.tesourotransparente.gov.br/',
          quarantinedCount: 0,
          numericTotal: 1000,
          valueKind: 'TRANSFER_AMOUNT_AS_PUBLISHED',
          financial: true,
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
    await fixture.whenStable();
    expect(fixture.nativeElement.textContent).toContain('Cobertura por fonte oficial');
    expect(fixture.nativeElement.textContent).toContain('O que foi publicado');
    expect(fixture.nativeElement.textContent).toContain('R$');
    expect(fixture.nativeElement.textContent).not.toContain('REFERENCE_QUANTITY');
    expect(fixture.nativeElement.textContent).not.toContain('REAL_OFFICIAL_DATA');
    expect(fixture.nativeElement.textContent).not.toContain('fpm_published');
    const button: HTMLButtonElement = fixture.nativeElement.querySelector('button.linkish');
    button.click();
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Lineage');
    expect(fixture.nativeElement.textContent).toContain('landing/manifest.json');
    expect(fixture.nativeElement.textContent).toContain('linhas 1');
    fixture.destroy();
    httpCtrl.verify();
  });
});
