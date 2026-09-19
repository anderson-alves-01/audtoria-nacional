import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type OpsGovernanceViewState = 'loading' | 'empty' | 'ok' | 'error';

export interface OpsRunbookItem {
  id: string;
  label: string;
  path: string;
  present: boolean;
}

@Component({
  selector: 'app-ops-governance-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './ops-governance-page.component.html',
  styleUrl: './ops-governance-page.component.scss',
})
export class OpsGovernancePageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: OpsGovernanceViewState = 'loading';
  disclaimer = '';
  version = '';
  g10Status = '';
  canDeploy = false;
  runbooks: OpsRunbookItem[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        canDeploy: boolean;
        canApprove: boolean;
        g10Status: string;
        runbooksComplete: boolean;
        runbooks: OpsRunbookItem[];
        disclaimer: string;
      }>('/v1/ops-governance')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.g10Status = body.g10Status;
          this.canDeploy = body.canDeploy;
          this.runbooks = body.runbooks;
          this.state = body.runbooks.length ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar a governança operacional.';
          this.state = 'error';
        },
      });
  }
}
