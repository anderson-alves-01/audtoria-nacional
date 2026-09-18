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
  errorMessage = '';

  ngOnInit(): void {
    this.http.get<{ items: SourceItem[] }>('/v1/data-sources').subscribe({
      next: (body) => {
        this.items = body.items;
        this.state = 'ok';
      },
      error: () => {
        this.errorMessage = 'Não foi possível carregar o catálogo sintético de fontes.';
        this.state = 'error';
      },
    });
  }
}
