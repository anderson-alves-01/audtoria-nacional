import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type StateTransfersViewState = 'loading' | 'empty' | 'ok' | 'error';

export interface StateTransferRow {
  uf: string;
  name: string;
  status: string;
  structuredOfficialSource: string | null;
  ingestAllowed: boolean;
}

@Component({
  selector: 'app-state-transfers-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './state-transfers-page.component.html',
  styleUrl: './state-transfers-page.component.scss',
})
export class StateTransfersPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: StateTransfersViewState = 'loading';
  disclaimer = '';
  version = '';
  ingestEnabled = false;
  createsTaxCredit = true;
  institutionalStatus = '';
  verifiedCount = 0;
  states: StateTransferRow[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        ingestEnabled: boolean;
        createsTaxCredit: boolean;
        institutionalStatus: string;
        verifiedCount: number;
        states: StateTransferRow[];
        items: unknown[];
        disclaimer: string;
      }>('/v1/state-transfers')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.ingestEnabled = body.ingestEnabled;
          this.createsTaxCredit = body.createsTaxCredit;
          this.institutionalStatus = body.institutionalStatus;
          this.verifiedCount = body.verifiedCount;
          this.states = body.states;
          this.state = body.items.length === 0 ? 'empty' : 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar as transferências estaduais.';
          this.state = 'error';
        },
      });
  }
}
