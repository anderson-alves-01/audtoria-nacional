import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type CalendarViewState = 'loading' | 'empty' | 'ok' | 'error';

export interface RegulatoryItemView {
  code: string;
  title: string;
  source: string;
  kind: string;
  status: string;
  binding: boolean;
  notes: string;
}

export interface PreservedDocumentView {
  sourceId: string;
  published: boolean;
  methodologyVersion: string | null;
  officialUrl: string | null;
  bronzeSha256: string | null;
  checksumSha256: string | null;
  landingManifestPath: string | null;
  binding: boolean;
  operational: boolean;
  homologated: boolean;
}

@Component({
  selector: 'app-calendar-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './calendar-page.component.html',
  styleUrl: './calendar-page.component.scss',
})
export class CalendarPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: CalendarViewState = 'loading';
  disclaimer = '';
  catalogVersion = '';
  operational = false;
  homologated = false;
  items: RegulatoryItemView[] = [];
  preservedDocuments: PreservedDocumentView[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        binding: boolean;
        operational: boolean;
        homologated: boolean;
        disclaimer: string;
        catalogVersion: string;
        preservedDocuments?: PreservedDocumentView[];
        items: RegulatoryItemView[];
      }>('/v1/regulatory/ibs-cbs')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.catalogVersion = body.catalogVersion;
          this.operational = body.operational;
          this.homologated = body.homologated;
          this.items = body.items;
          this.preservedDocuments = body.preservedDocuments ?? [];
          this.state = body.items.length ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o calendário IBS/CBS.';
          this.state = 'error';
        },
      });
  }
}
