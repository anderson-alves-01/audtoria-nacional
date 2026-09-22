import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription, catchError, from, of, switchMap } from 'rxjs';
import { PublicOpenSessionService } from '../auth/public-open-session.service';
import { ChartCardComponent, ChartSeriesInput } from '../shared/charts/chart-card.component';
import { EvidenceDrawerComponent } from '../shared/evidence/evidence-drawer.component';
import { EmptyStateComponent } from '../shared/states/empty-state.component';
import { ErrorStateComponent } from '../shared/states/error-state.component';
import { SkeletonComponent } from '../shared/states/skeleton.component';
import { KpiCardComponent } from '../shared/ui/kpi-card.component';

export type DashboardViewState = 'loading' | 'empty' | 'ok' | 'partial' | 'error';

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
  type: string;
  unit: string;
  valueKind: string;
  series: { name: string; points: ChartPoint[] }[];
  evidenceIds: string[];
}

interface ChartView {
  id: string;
  title: string;
  summary: string;
  unit: string;
  valueKind: string;
  chartType: 'line' | 'bar';
  series: ChartSeriesInput;
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
          this.resetView(String(data['dashboardId'] || ''));
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

  formatKpi(value: number, unit: string): string {
    if (unit === 'BRL') {
      return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }
    return value.toLocaleString('pt-BR');
  }

  private resetView(dashboardId: string): void {
    this.dashboardId = dashboardId;
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
    this.chartViews = (body.charts || []).map((chart) => this.toChartView(chart));
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
    const summary = `${chart.title}: ${points.length} pontos; valueKind ${chart.valueKind}.`;
    return {
      id: chart.id,
      title: chart.title,
      summary,
      unit: chart.unit,
      valueKind: chart.valueKind,
      chartType: chart.type === 'line' ? 'line' : 'bar',
      series: { name: series?.name || chart.title, points },
    };
  }
}
