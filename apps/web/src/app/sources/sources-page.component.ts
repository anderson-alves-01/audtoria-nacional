import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

interface SourceItem {
  sourceId: string;
  name: string;
  sourceRole: string;
  accessClassification: string;
  status: string;
  ingestAllowed: boolean;
  createsTaxCredit: boolean;
  fixtureKind?: string;
}

interface EnrichmentView {
  sourceId: string;
  sourceRole?: string;
  published: boolean;
  indicatorCount: number;
  createsTaxCredit: boolean;
  banner?: string;
  homologationStatus?: string;
  emptyReason?: string;
  officialUrl?: string;
  competence?: string;
  formula?: string;
  methodologyVersion?: string;
  qualityLevel?: string;
  quarantinedCount?: number;
  note?: string;
}

@Component({
  selector: 'app-sources-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sources-page.component.html',
  styleUrl: './sources-page.component.scss',
})
export class SourcesPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: 'loading' | 'ok' | 'error' = 'loading';
  items: SourceItem[] = [];
  enrichment: EnrichmentView | null = null;
  ingestMessage = '';
  errorMessage = '';
  readonly banner =
    'DADOS DE FONTE OFICIAL — PROCESSAMENTO TÉCNICO CONCLUÍDO — HOMOLOGAÇÃO HUMANA PENDENTE';

  ngOnInit(): void {
    this.http.get<{ items: SourceItem[] }>('/v1/data-sources').subscribe({
      next: (body) => {
        this.items = body.items;
        this.state = 'ok';
        this.loadEnrichment('IBGE-SIDRA');
      },
      error: () => {
        this.errorMessage = 'Não foi possível carregar o catálogo oficial de fontes.';
        this.state = 'error';
      },
    });
  }

  ingest(item: SourceItem): void {
    this.ingestMessage = '';
    this.http.post(`/v1/data-sources/${item.sourceId}/ingest`, {}).subscribe({
      next: () => {
        this.ingestMessage = `Fonte oficial ${item.sourceId} ingerida. Nenhum crédito tributário foi criado.`;
        this.loadEnrichment(item.sourceId);
      },
      error: () => {
        this.ingestMessage = `Ingestão recusada ou indisponível para ${item.sourceId}.`;
      },
    });
  }

  private loadEnrichment(sourceId: string): void {
    this.http
      .get<EnrichmentView>('/v1/indicators/source-enrichment', { params: { sourceId } })
      .subscribe({
        next: (body) => {
          this.enrichment = body;
        },
        error: () => {
          this.enrichment = null;
        },
      });
  }
}
