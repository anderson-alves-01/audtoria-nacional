import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type FunnelViewState = 'loading' | 'empty' | 'ok' | 'error';

interface OfficialGoldItem {
  sourceId: string;
  indicator: string;
  maintainer: string;
  dataset: string;
  competence: string;
  lastExtractedAt: string;
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
  selector: 'app-funnel-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './funnel-page.component.html',
  styleUrl: './funnel-page.component.scss',
})
export class FunnelPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: FunnelViewState = 'loading';
  items: OfficialGoldItem[] = [];
  emptySources: { sourceId: string; emptyReason?: string; status?: string }[] = [];
  banner = '';
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        published: boolean;
        banner: string;
        items: OfficialGoldItem[];
        emptySources: { sourceId: string; emptyReason?: string; status?: string }[];
      }>('/v1/indicators/official-gold')
      .subscribe({
        next: (body) => {
          this.items = body.items || [];
          this.emptySources = body.emptySources || [];
          this.banner = body.banner;
          this.state = body.published ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar os indicadores oficiais.';
          this.state = 'error';
        },
      });
  }
}
