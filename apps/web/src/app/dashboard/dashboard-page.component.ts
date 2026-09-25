import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription, catchError, from, of, switchMap } from 'rxjs';
import { PublicOpenSessionService } from '../auth/public-open-session.service';
import { BrazilRegionMapComponent } from './brazil-region-map.component';
import { ChartCardComponent, ChartSeriesInput } from '../shared/charts/chart-card.component';
import { EvidenceDrawerComponent } from '../shared/evidence/evidence-drawer.component';
import {
  formatPublishedValue,
  humanizeAxis,
  humanizeHomologation,
  humanizeIndicator,
  humanizeProse,
  humanizeQuality,
  humanizeSource,
  humanizeValueKind,
} from '../shared/presentation/official-labels';
import { EmptyStateComponent } from '../shared/states/empty-state.component';
import { ErrorStateComponent } from '../shared/states/error-state.component';
import { SkeletonComponent } from '../shared/states/skeleton.component';
import { KpiCardComponent } from '../shared/ui/kpi-card.component';

export type DashboardViewState = 'loading' | 'empty' | 'ok' | 'partial' | 'error';

interface PublishedMeasure {
  label: string;
  value: number;
  unit: string;
  count?: number;
}

interface DashboardGoldItem {
  sourceId: string;
  indicator: string;
  maintainer: string;
  dataset: string;
  competence: string;
  formula: string;
  methodologyVersion: string;
  coverageCount: number;
  qualityLevel: string;
  homologationStatus: string;
  officialUrl: string;
  quarantinedCount: number;
  numericTotal: number | null;
  valueKind?: string;
  presentation?: string;
  financial?: boolean;
  measures?: PublishedMeasure[];
  lineageLineCount?: number;
  goldId?: string;
  lineage?: {
    bronzeSha256?: string;
    landingPath?: string;
    landingManifestPath?: string;
    endpoint?: string;
  };
}

interface EmptySource {
  sourceId: string;
  emptyReason?: string;
  status?: string;
  competence?: string;
  formula?: string;
  officialUrl?: string;
  qualityLevel?: string;
  homologationStatus?: string;
}

interface DashboardKpi {
  id: string;
  label: string;
  value: number;
  unit: string;
  valueKind: string;
  sourceId: string;
  evidenceId?: string | null;
}

interface ChartPoint {
  x: string;
  y: number;
}

interface DashboardChart {
  id: string;
  title: string;
  note?: string;
  type: string;
  unit: string;
  valueKind: string;
  sourceId?: string;
  series: { name: string; points: ChartPoint[] }[];
  evidenceIds: string[];
}

interface ChartView {
  id: string;
  title: string;
  summary: string;
  unit: string;
  valueKind: string;
  sourceId: string;
  chartType: 'line' | 'bar';
  series: ChartSeriesInput;
}

interface PublishedReading {
  key: string;
  title: string;
  measures: PublishedMeasure[];
  figure: string;
  presentation: string;
  valueKind: string;
  maintainer: string;
  competence: string;
  coverageCount: number;
  qualityLevel: string;
  homologationStatus: string;
  formula: string;
}

interface DashboardResponse {
  title: string;
  banner: string;
  emptyReason: string;
  published: boolean;
  commandsDisabled: boolean;
  homologationStatus: string;
  items: DashboardGoldItem[];
  emptySources: EmptySource[];
  kpis?: DashboardKpi[];
  charts?: DashboardChart[];
}

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [
    CommonModule,
    BrazilRegionMapComponent,
    KpiCardComponent,
    ChartCardComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    SkeletonComponent,
    EvidenceDrawerComponent,
  ],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.scss',
})
export class DashboardPageComponent implements OnInit, OnDestroy {
  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);
  private readonly session = inject(PublicOpenSessionService);
  private sub?: Subscription;

  state: DashboardViewState = 'loading';
  dashboardId = '';
  pageTitle = '';
  title = '';
  banner = '';
  emptyReason = '';
  homologationStatus = '';
  items: DashboardGoldItem[] = [];
  emptySources: EmptySource[] = [];
  kpis: DashboardKpi[] = [];
  chartViews: ChartView[] = [];
  errorMessage = '';
  correlationId = '';
  commandsDisabled = true;
  lineageOpen = false;

  ngOnInit(): void {
    this.sub = this.route.data
      .pipe(
        switchMap((data) => {
          this.resetView(String(data['dashboardId'] || ''), String(data['title'] || ''));
          return from(this.session.ensureSession()).pipe(
            switchMap(() => this.http.get<DashboardResponse>(`/v1/dashboards/${this.dashboardId}`)),
            catchError((err: HttpErrorResponse) => {
              this.applyError(err);
              return of(null);
            }),
          );
        }),
      )
      .subscribe((body) => {
        if (body) {
          this.applyBody(body);
        }
      });
  }

  ngOnDestroy(): void {
    this.sub?.unsubscribe();
  }

  toggleLineage(): void {
    this.lineageOpen = !this.lineageOpen;
  }

  readonly humanizeValueKind = humanizeValueKind;

  sourceHeading(sourceId: string): string {
    return humanizeSource(sourceId);
  }

  prose(text: string | null | undefined): string {
    return humanizeProse(text);
  }

  panelSources(): string {
    const names = [...new Set(this.items.map((item) => humanizeSource(item.sourceId)))];
    return names.slice(0, 3).join('; ');
  }

  formatKpi(value: number, unit: string): string {
    return formatPublishedValue(value, unit);
  }

  indicatorTitle(item: DashboardGoldItem): string {
    return humanizeIndicator(item.indicator, item.presentation);
  }

  kpiTitle(kpi: DashboardKpi): string {
    const item = this.items.find((entry) => entry.sourceId === kpi.sourceId);
    if (kpi.label.startsWith('Cobertura ')) {
      return `Registros na base · ${humanizeSource(kpi.sourceId)}`;
    }
    if (kpi.label.includes(' ') && !kpi.label.includes('_')) {
      return kpi.label;
    }
    return humanizeIndicator(kpi.label, item?.presentation);
  }

  kpiMeta(kpi: DashboardKpi): string {
    const item = this.items.find((entry) => entry.sourceId === kpi.sourceId);
    const source = humanizeSource(kpi.sourceId);
    const competence = item?.competence ? `competência ${item.competence}` : '';
    const officialUnit =
      kpi.unit && !['BRL', 'COUNT', 'UNIT', 'MIXED'].includes(kpi.unit) ? kpi.unit : '';
    return [source, competence, officialUnit].filter((part) => part.length > 0).join(' · ');
  }

  kpiKind(kpi: DashboardKpi): string {
    return humanizeValueKind(kpi.valueKind);
  }

  validationText(status: string | null | undefined): string {
    return humanizeHomologation(status || this.homologationStatus);
  }

  qualityText(level: string | null | undefined): string {
    return humanizeQuality(level);
  }

  publishedTotal(item: DashboardGoldItem): string {
    const unit = item.financial ? 'BRL' : 'UNIT';
    return formatPublishedValue(item.numericTotal, unit);
  }

  publishedReadings(): PublishedReading[] {
    const groups = new Map<string, DashboardGoldItem[]>();
    for (const item of this.items) {
      const bucket = groups.get(item.sourceId) ?? [];
      bucket.push(item);
      groups.set(item.sourceId, bucket);
    }
    return [...groups.entries()].map(([sourceId, group]) => this.readingFor(sourceId, group));
  }

  private readingFor(sourceId: string, group: DashboardGoldItem[]): PublishedReading {
    const withFigure = group.find(
      (item) => item.numericTotal != null || (item.measures?.length ?? 0) > 1,
    );
    const head = withFigure ?? group[0];
    const measures = this.separateMeasures(head);
    const chartMoney = this.chartViews.some((chart) => chart.sourceId === sourceId && chart.unit === 'BRL');
    const competences = [...new Set(group.map((item) => item.competence).filter((value) => value))];
    const newest = competences[0] || head.competence;
    const oldest = competences[competences.length - 1] || head.competence;
    const competence =
      competences.length > 1 ? `${oldest} a ${newest}` : newest;
    let figure = measures.length ? '' : this.publishedTotal(head);
    let presentation =
      this.prose(head.presentation) || 'Leitura do valor publicado pelo órgão. Não é crédito tributário.';
    if (!measures.length && head.numericTotal == null && chartMoney) {
      figure = 'Valores da conta-mãe publicados nos gráficos desta fonte.';
      presentation =
        'A lista não soma todas as contas do demonstrativo. O gráfico mostra a conta-mãe já publicada. Não é o total nacional e não é valor a recuperar.';
    }
    const title =
      group.length > 1 && head.numericTotal == null
        ? this.sourceHeading(sourceId)
        : this.indicatorTitle(head);
    return {
      key: sourceId,
      title,
      measures,
      figure,
      presentation,
      valueKind: head.valueKind || '',
      maintainer: head.maintainer,
      competence,
      coverageCount: head.coverageCount,
      qualityLevel: head.qualityLevel,
      homologationStatus: head.homologationStatus,
      formula: head.formula,
    };
  }

  separateMeasures(item: DashboardGoldItem): PublishedMeasure[] {
    return item.measures && item.measures.length > 1 ? item.measures : [];
  }

  formatMeasure(measure: PublishedMeasure): string {
    const figure = formatPublishedValue(measure.value, measure.unit === 'BRL' ? 'BRL' : 'UNIT');
    if (!measure.unit || measure.unit === 'BRL' || measure.unit === 'UNIT' || measure.unit === 'COUNT') {
      return figure;
    }
    return `${figure} ${measure.unit}`;
  }

  private resetView(dashboardId: string, pageTitle = ''): void {
    this.dashboardId = dashboardId;
    this.pageTitle = pageTitle;
    this.state = 'loading';
    this.title = '';
    this.banner = '';
    this.emptyReason = '';
    this.homologationStatus = '';
    this.items = [];
    this.emptySources = [];
    this.kpis = [];
    this.chartViews = [];
    this.errorMessage = '';
    this.correlationId = '';
    this.lineageOpen = false;
    this.commandsDisabled = true;
  }

  private applyBody(body: DashboardResponse): void {
    this.title = body.title;
    this.banner = body.banner;
    this.emptyReason = body.emptyReason;
    this.homologationStatus = body.homologationStatus;
    this.items = body.items || [];
    this.emptySources = body.emptySources || [];
    this.kpis = body.kpis || [];
    this.chartViews = (body.charts || [])
      .filter((chart) => chart.unit !== 'MIXED')
      .map((chart) => this.toChartView(chart));
    this.commandsDisabled = body.commandsDisabled;
    if (!body.published) {
      this.state = 'empty';
    } else if (this.emptySources.length) {
      this.state = 'partial';
    } else {
      this.state = 'ok';
    }
  }

  private applyError(err: HttpErrorResponse): void {
    this.correlationId = err.headers?.get('x-trace-id') || err.headers?.get('x-correlation-id') || '';
    if (err.status === 401 || err.status === 403) {
      this.errorMessage =
        'Não autorizado a carregar o painel. Sessão PUBLIC_OPEN ausente ou inválida.';
    } else {
      this.errorMessage = 'Não foi possível carregar o painel oficial.';
    }
    this.state = 'error';
  }

  private toChartView(chart: DashboardChart): ChartView {
    const series = chart.series?.[0];
    const points = series?.points || [];
    const caution =
      chart.unit === 'MIXED'
        ? ' Pontos de naturezas diferentes ficam no mesmo eixo e não formam um total único.'
        : '';
    const pointWord = points.length === 1 ? 'ponto publicado' : 'pontos publicados';
    const note = chart.note ? ` ${chart.note}` : '';
    const kind = humanizeValueKind(chart.valueKind);
    const summary = `${chart.title}: ${points.length} ${pointWord}. ${kind}.${caution}${note}`;
    return {
      id: chart.id,
      title: chart.title,
      summary,
      unit: chart.unit,
      valueKind: chart.valueKind,
      sourceId: chart.sourceId || '',
      chartType: chart.type === 'line' ? 'line' : 'bar',
      series: {
        name: series?.name || chart.title,
        points: points.map((point) => ({ ...point, x: this.axisLabel(point.x) })),
      },
    };
  }

  private axisLabel(value: string): string {
    if (/^\d{6,7}$/.test(value)) {
      return `Município ${value}`;
    }
    return humanizeAxis(value);
  }
}
