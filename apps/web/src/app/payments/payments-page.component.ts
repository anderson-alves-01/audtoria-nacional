import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type PaymentsViewState = 'loading' | 'empty' | 'ok' | 'error';

@Component({
  selector: 'app-payments-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './payments-page.component.html',
  styleUrl: './payments-page.component.scss',
})
export class PaymentsPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: PaymentsViewState = 'loading';
  disclaimer = '';
  version = '';
  credentialStatus = '';
  g6Status = '';
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        commandsDisabled: boolean;
        recoveryInvented: boolean;
        createsTaxCredit: boolean;
        credentialStatus: string;
        g6Status: string;
        items: unknown[];
        installments: unknown[];
        disclaimer: string;
      }>('/v1/payments')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.credentialStatus = body.credentialStatus;
          this.g6Status = body.g6Status;
          const empty = body.items.length === 0 && body.installments.length === 0;
          this.state = empty ? 'empty' : 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o painel de pagamentos.';
          this.state = 'error';
        },
      });
  }
}
