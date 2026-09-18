import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type FunnelViewState = 'loading' | 'empty' | 'ok' | 'error';

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
  identified = 0;
  validated = 0;
  inCollection = 0;
  methodology = '';
  note = '';
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        identifiedCount: number;
        validatedCount: number;
        inCollectionCount: number;
        methodologyVersion: string;
        published: boolean;
        note: string;
      }>('/v1/indicators/credit-funnel')
      .subscribe({
        next: (body) => {
          this.identified = body.identifiedCount;
          this.validated = body.validatedCount;
          this.inCollection = body.inCollectionCount;
          this.methodology = body.methodologyVersion;
          this.note = body.note;
          this.state = body.published ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o funil sintético.';
          this.state = 'error';
        },
      });
  }
}
