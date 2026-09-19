import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type DiagnosisViewState = 'loading' | 'empty' | 'ok' | 'error';

export interface DiagnosisChecklistItem {
  id: string;
  label: string;
  met: boolean;
}

@Component({
  selector: 'app-diagnosis-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './diagnosis-page.component.html',
  styleUrl: './diagnosis-page.component.scss',
})
export class DiagnosisPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: DiagnosisViewState = 'loading';
  disclaimer = '';
  version = '';
  g1Status = '';
  checklist: DiagnosisChecklistItem[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        binding: boolean;
        operational: boolean;
        homologated: boolean;
        commandsDisabled: boolean;
        recoveryMeta: null;
        g1Status: string;
        checklist: DiagnosisChecklistItem[];
        items: unknown[];
        disclaimer: string;
      }>('/v1/diagnosis')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.g1Status = body.g1Status;
          this.checklist = body.checklist;
          this.state = body.checklist.length ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o diagnóstico técnico.';
          this.state = 'error';
        },
      });
  }
}
