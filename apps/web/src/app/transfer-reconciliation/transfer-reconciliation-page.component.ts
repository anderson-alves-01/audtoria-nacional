import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type TransferReconciliationViewState = 'loading' | 'empty' | 'ok' | 'error';

@Component({
  selector: 'app-transfer-reconciliation-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './transfer-reconciliation-page.component.html',
  styleUrl: './transfer-reconciliation-page.component.scss',
})
export class TransferReconciliationPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: TransferReconciliationViewState = 'loading';
  disclaimer = '';
  version = '';
  g7Status = '';
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        commandsDisabled: boolean;
        autoReconcileEnabled: boolean;
        createsTaxCredit: boolean;
        differenceIsOccurrenceOnly: boolean;
        g7Status: string;
        items: unknown[];
        differences: unknown[];
        disclaimer: string;
      }>('/v1/transfer-reconciliation')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.g7Status = body.g7Status;
          const empty = body.items.length === 0 && body.differences.length === 0;
          this.state = empty ? 'empty' : 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar a conciliação de transferências.';
          this.state = 'error';
        },
      });
  }
}
