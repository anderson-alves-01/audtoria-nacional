import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type GatesViewState = 'loading' | 'ok' | 'error';

export interface GateChecklistItem {
  id: string;
  label: string;
  met: boolean;
}

export interface GateView {
  id: string;
  component: string;
  status?: string;
  localStatus?: string;
  officialStatus?: string;
  checklist?: GateChecklistItem[];
}

@Component({
  selector: 'app-gates-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './gates-page.component.html',
  styleUrl: './gates-page.component.scss',
})
export class GatesPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: GatesViewState = 'loading';
  gates: GateView[] = [];
  canApprove = false;
  humanApprovalFabricated = false;
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        gates: GateView[];
        canApprove: boolean;
        humanApprovalFabricated: boolean;
      }>('/v1/program-gates')
      .subscribe({
        next: (body) => {
          this.gates = body.gates;
          this.canApprove = body.canApprove;
          this.humanApprovalFabricated = body.humanApprovalFabricated;
          this.state = 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o snapshot de gates.';
          this.state = 'error';
        },
      });
  }
}
