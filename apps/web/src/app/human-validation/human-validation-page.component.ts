import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type HumanValidationViewState = 'loading' | 'empty' | 'ok' | 'error';

@Component({
  selector: 'app-human-validation-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './human-validation-page.component.html',
  styleUrl: './human-validation-page.component.scss',
})
export class HumanValidationPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: HumanValidationViewState = 'loading';
  disclaimer = '';
  version = '';
  g4Status = '';
  g5Status = '';
  referenceStates: string[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        commandsDisabled: boolean;
        createsTaxCredit: boolean;
        publishesPublicCredit: boolean;
        g4Status: string;
        g5Status: string;
        referenceStates: string[];
        activeItems: unknown[];
        queue: unknown[];
        disclaimer: string;
      }>('/v1/human-validation')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.g4Status = body.g4Status;
          this.g5Status = body.g5Status;
          this.referenceStates = body.referenceStates;
          const empty = body.activeItems.length === 0 && body.queue.length === 0;
          this.state = empty ? 'empty' : 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar a validação humana.';
          this.state = 'error';
        },
      });
  }
}
