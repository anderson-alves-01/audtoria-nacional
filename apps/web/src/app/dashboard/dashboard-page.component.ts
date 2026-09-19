import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

export type DashboardViewState = 'loading' | 'empty' | 'ok' | 'error';

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
}

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.scss',
})
export class DashboardPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);
  state: DashboardViewState = 'loading';
  title = '';
  banner = '';
  emptyReason = '';
  items: DashboardGoldItem[] = [];
  errorMessage = '';
  commandsDisabled = true;

  ngOnInit(): void {
    const dashboardId = this.route.snapshot.data['dashboardId'] as string;
    this.http.get<{
      title: string;
      banner: string;
      emptyReason: string;
      published: boolean;
      commandsDisabled: boolean;
      items: DashboardGoldItem[];
    }>(`/v1/dashboards/${dashboardId}`).subscribe({
      next: (body) => {
        this.title = body.title;
        this.banner = body.banner;
        this.emptyReason = body.emptyReason;
        this.items = body.items || [];
        this.commandsDisabled = body.commandsDisabled;
        this.state = body.published ? 'ok' : 'empty';
      },
      error: () => {
        this.errorMessage = 'Não foi possível carregar o painel oficial.';
        this.state = 'error';
      },
    });
  }
}
