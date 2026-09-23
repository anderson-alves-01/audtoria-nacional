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

  it('keeps distinct measures apart and drops mixed charts', async () => {
    const fixture = TestBed.createComponent(DashboardPageComponent);
    const httpCtrl = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    await fixture.whenStable();
    httpCtrl.expectOne('/v1/dashboards/transferencias').flush({
      title: 'Transferências',
      banner: 'DADOS DE FONTE OFICIAL — REFERÊNCIA HUMANAMENTE VALIDADA — NÃO É CRÉDITO TRIBUTÁRIO',
      emptyReason: '',
      published: true,
      commandsDisabled: true,
      homologationStatus: 'REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY',
      emptySources: [],
      kpis: [],
      charts: [
        {
          id: 'mixed',
          title: 'Total publicado por competência',
          type: 'bar',
          unit: 'MIXED',
          valueKind: 'REFERENCE_QUANTITY',
          series: [{ name: 'Total', points: [{ x: '2024', y: 1 }] }],
          evidenceIds: [],
        },
      ],
      items: [
        {
          sourceId: 'IBGE-SIDRA-CEMP',
          indicator: 'ibge_cemp_municipal_totals',
          maintainer: 'IBGE',
          dataset: 'SIDRA-9509',
          competence: '2024',
          formula: 'Variáveis separadas.',
          methodologyVersion: 'v1',
          coverageCount: 2,
          qualityLevel: 'TECHNICALLY_VALIDATED',
          homologationStatus: 'REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY',
          officialUrl: 'https://sidra.ibge.gov.br/',
          quarantinedCount: 0,
          numericTotal: 999,
          valueKind: 'REFERENCE_QUANTITY',
          financial: false,
          measures: [
            { label: 'Pessoal ocupado', value: 10, unit: 'Pessoas' },
            { label: 'Salários', value: 20, unit: 'Mil Reais' },
          ],
        },
      ],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Pessoal ocupado');
    expect(text).toContain('Salários');
    expect(text).toContain('Mil Reais');
    expect(text).not.toContain('Total publicado por competência');
    expect(text).not.toContain('999');
    fixture.destroy();
    httpCtrl.verify();
  });

  it('collapses statement lines without a total when the revenue chart already has the figure', async () => {
    const fixture = TestBed.createComponent(DashboardPageComponent);
    const httpCtrl = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    await fixture.whenStable();
    httpCtrl.expectOne('/v1/dashboards/transferencias').flush({
      title: 'Financeiro e ROI',
      banner: 'DADOS DE FONTE OFICIAL — REFERÊNCIA HUMANAMENTE VALIDADA — NÃO É CRÉDITO TRIBUTÁRIO',
      emptyReason: '',
      published: true,
      commandsDisabled: true,
      homologationStatus: 'REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY',
      emptySources: [],
      kpis: [],
      charts: [
        {
          id: 'revenue-siconfi-rreo',
          title: 'Receita corrente — até o bimestre',
          type: 'bar',
          unit: 'BRL',
          valueKind: 'FISCAL_STATEMENT_LINE',
          sourceId: 'SICONFI-RREO',
          note: 'Soma das linhas de receita já publicadas nesta carga. Não é o total nacional e não é valor a recuperar.',
          series: [{ name: 'Até o bimestre', points: [{ x: '2025', y: 80 }] }],
          evidenceIds: [],
        },
      ],
      items: [
        {
          sourceId: 'SICONFI-RREO',
          indicator: 'siconfi_rreo_lines',
          maintainer: 'Tesouro Nacional',
          dataset: 'SICONFI-RREO',
          competence: '2025',
          formula: 'Conta-mãe publicada.',
          methodologyVersion: 'v1',
          coverageCount: 2144,
          qualityLevel: 'TECHNICALLY_VALIDATED',
          homologationStatus: 'REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY',
          officialUrl: 'https://siconfi.tesouro.gov.br/',
          quarantinedCount: 0,
          numericTotal: null,
          valueKind: 'FISCAL_STATEMENT_LINE',
          presentation: 'Linhas do RREO municipal.',
          financial: false,
        },
        {
          sourceId: 'SICONFI-RREO',
          indicator: 'siconfi_rreo_lines_prior',
          maintainer: 'Tesouro Nacional',
          dataset: 'SICONFI-RREO',
          competence: '2024',
          formula: 'Conta-mãe publicada.',
          methodologyVersion: 'v1',
          coverageCount: 1000,
          qualityLevel: 'TECHNICALLY_VALIDATED',
          homologationStatus: 'REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY',
          officialUrl: 'https://siconfi.tesouro.gov.br/',
          quarantinedCount: 0,
          numericTotal: null,
          valueKind: 'FISCAL_STATEMENT_LINE',
          presentation: 'Linhas do RREO municipal.',
          financial: false,
        },
      ],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Valores da conta-mãe publicados nos gráficos desta fonte.');
    expect(text).toContain('2024 a 2025');
    expect(text).not.toContain('Valor não publicado');
    expect(fixture.nativeElement.querySelectorAll('.source-list li').length).toBe(1);
    fixture.destroy();
    httpCtrl.verify();
  });
});
