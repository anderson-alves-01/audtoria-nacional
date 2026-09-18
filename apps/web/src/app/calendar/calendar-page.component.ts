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
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        binding: boolean;
        operational: boolean;
        homologated: boolean;
        disclaimer: string;
        catalogVersion: string;
        items: RegulatoryItemView[];
      }>('/v1/regulatory/ibs-cbs')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.catalogVersion = body.catalogVersion;
          this.operational = body.operational;
          this.homologated = body.homologated;
          this.items = body.items;
          this.state = body.items.length ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o calendário sintético IBS/CBS.';
          this.state = 'error';
        },
      });
  }
}
