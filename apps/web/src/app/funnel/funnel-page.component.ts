import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { EmptyStateComponent } from '../shared/states/empty-state.component';

export type FunnelViewState = 'loading' | 'empty' | 'ok' | 'error';

interface CreditFunnelResponse {
  identifiedCount: number;
  validatedCount: number;
  inCollectionCount: number;
  silverRowCount: number;
  published: boolean;
}

interface FunnelStage {
  id: string;
  label: string;
  figure: string;
  note: string;
}

@Component({
  selector: 'app-funnel-page',
  standalone: true,
  imports: [CommonModule, EmptyStateComponent],
  templateUrl: './funnel-page.component.html',
  styleUrl: './funnel-page.component.scss',
})
export class FunnelPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: FunnelViewState = 'loading';
  stages: FunnelStage[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http.get<CreditFunnelResponse>('/v1/indicators/credit-funnel').subscribe({
      next: (body) => {
        if (!body.published) {
          this.stages = [];
          this.state = 'empty';
          return;
        }
        this.stages = [
          this.stage('identified', 'Identificado', body.identifiedCount, 'Contagem publicada. Não é valor em reais.'),
          this.stage('validated', 'Validado', body.validatedCount, 'Contagem publicada. Não autoriza cobrança.'),
          this.stage(
            'collection',
            'Em cobrança',
            body.inCollectionCount,
            'Contagem publicada. Não é crédito constituído por este painel.',
          ),
        ];
        if (body.silverRowCount > 0) {
          this.stages.push(
            this.stage(
              'support',
              'Linhas de apoio na carga',
              body.silverRowCount,
              'Contagem de linhas da carga. Não é arrecadação nem valor a recuperar.',
            ),
          );
        }
        this.state = 'ok';
      },
      error: () => {
        this.errorMessage = 'Não foi possível carregar o funil de recuperação.';
        this.state = 'error';
      },
    });
  }

  private stage(id: string, label: string, count: number, note: string): FunnelStage {
    return {
      id,
      label,
      figure: Number(count || 0).toLocaleString('pt-BR'),
      note,
    };
  }
}
