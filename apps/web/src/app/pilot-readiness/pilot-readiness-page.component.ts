import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type PilotReadinessViewState = 'loading' | 'empty' | 'ok' | 'error';

export interface PilotChecklistItem {
  id: string;
  label: string;
  met: boolean;
  category: string;
}

@Component({
  selector: 'app-pilot-readiness-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pilot-readiness-page.component.html',
  styleUrl: './pilot-readiness-page.component.scss',
})
export class PilotReadinessPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: PilotReadinessViewState = 'loading';
  disclaimer = '';
  version = '';
  g9Status = '';
  technicalReady = false;
  institutionalReady = false;
  checklist: PilotChecklistItem[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        technicalReady: boolean;
        institutionalReady: boolean;
        pilotMunicipalityApproved: boolean;
        g9Status: string;
        checklist: PilotChecklistItem[];
        disclaimer: string;
      }>('/v1/pilot-readiness')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.g9Status = body.g9Status;
          this.technicalReady = body.technicalReady;
          this.institutionalReady = body.institutionalReady;
          this.checklist = body.checklist;
          this.state = body.checklist.length ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar a prontidão de piloto.';
          this.state = 'error';
        },
      });
  }
}
