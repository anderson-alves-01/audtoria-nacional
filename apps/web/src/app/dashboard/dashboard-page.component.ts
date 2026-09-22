import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { EChartsOption } from 'echarts';
import { NgxEchartsDirective, provideEcharts } from 'ngx-echarts';
import { Subscription, switchMap, from, catchError, of } from 'rxjs';
import { PublicOpenSessionService } from '../auth/public-open-session.service';

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
  options: EChartsOption;
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
  imports: [CommonModule, NgxEchartsDirective],
  providers: [provideEcharts()],
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
    const categories = series?.points?.map((point) => point.x) || [];
    const values = series?.points?.map((point) => point.y) || [];
    const summary = `${chart.title}: ${values.length} pontos; valueKind ${chart.valueKind}.`;
    const options: EChartsOption = {
      color: ['#0f6a6a', '#1b4f72', '#b45309'],
      tooltip: { trigger: 'axis' },
      grid: { left: 48, right: 16, top: 28, bottom: 48 },
      xAxis: {
        type: 'category',
        data: categories,
        axisLabel: { color: '#3d4f5c', rotate: categories.length > 6 ? 35 : 0 },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#3d4f5c' },
        splitLine: { lineStyle: { color: '#d7e2e8' } },
      },
      series: [
        {
          name: series?.name || chart.title,
          type: chart.type === 'line' ? 'line' : 'bar',
          data: values,
          barMaxWidth: 36,
        },
      ],
    };
    return { id: chart.id, title: chart.title, summary, options };
  }
}
