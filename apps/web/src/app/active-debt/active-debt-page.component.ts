import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type ActiveDebtViewState = 'loading' | 'empty' | 'ok' | 'error';

@Component({
  selector: 'app-active-debt-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './active-debt-page.component.html',
  styleUrl: './active-debt-page.component.scss',
})
export class ActiveDebtPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: ActiveDebtViewState = 'loading';
  disclaimer = '';
  version = '';
  credentialStatus = '';
  g0Status = '';
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        commandsDisabled: boolean;
        inscriptionEnabled: boolean;
        createsTaxCredit: boolean;
        credentialStatus: string;
        g0Status: string;
        items: unknown[];
        queue: unknown[];
        disclaimer: string;
      }>('/v1/active-debt')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.credentialStatus = body.credentialStatus;
          this.g0Status = body.g0Status;
          const empty = body.items.length === 0 && body.queue.length === 0;
          this.state = empty ? 'empty' : 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o painel de dívida ativa.';
          this.state = 'error';
        },
      });
  }
}
