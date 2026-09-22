import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type SectoralEnrichmentViewState = 'loading' | 'empty' | 'ok' | 'error';

export interface SectoralSourceRow {
  sourceId: string;
  maintainer: string;
  status: string;
  ingestAllowed: boolean;
  structuredOfficialSource: string;
}

@Component({
  selector: 'app-sectoral-enrichment-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sectoral-enrichment-page.component.html',
  styleUrl: './sectoral-enrichment-page.component.scss',
})
export class SectoralEnrichmentPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: SectoralEnrichmentViewState = 'loading';
  disclaimer = '';
  version = '';
  ingestEnabled = false;
  createsTaxCredit = true;
  institutionalStatus = '';
  sources: SectoralSourceRow[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        ingestEnabled: boolean;
        createsTaxCredit: boolean;
        institutionalStatus: string;
        sources: SectoralSourceRow[];
        items: unknown[];
        disclaimer: string;
      }>('/v1/sectoral-enrichment')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.ingestEnabled = body.ingestEnabled;
          this.createsTaxCredit = body.createsTaxCredit;
          this.institutionalStatus = body.institutionalStatus;
          this.sources = body.sources;
          this.state = body.items.length === 0 ? 'empty' : 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o enriquecimento setorial.';
          this.state = 'error';
        },
      });
  }
}
