import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type ProcuradoriaViewState = 'loading' | 'empty' | 'ok' | 'error';

@Component({
  selector: 'app-procuradoria-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './procuradoria-page.component.html',
  styleUrl: './procuradoria-page.component.scss',
})
export class ProcuradoriaPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: ProcuradoriaViewState = 'loading';
  disclaimer = '';
  version = '';
  g6Status = '';
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        commandsDisabled: boolean;
        legalCommandsEnabled: boolean;
        altersLegalStatus: boolean;
        createsTaxCredit: boolean;
        g6Status: string;
        items: unknown[];
        queue: unknown[];
        disclaimer: string;
      }>('/v1/procuradoria')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.g6Status = body.g6Status;
          const empty = body.items.length === 0 && body.queue.length === 0;
          this.state = empty ? 'empty' : 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o workflow da Procuradoria.';
          this.state = 'error';
        },
      });
  }
}
