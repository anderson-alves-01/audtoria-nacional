import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type CollectionViewState = 'loading' | 'empty' | 'ok' | 'error';

@Component({
  selector: 'app-collection-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './collection-page.component.html',
  styleUrl: './collection-page.component.scss',
})
export class CollectionPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: CollectionViewState = 'loading';
  disclaimer = '';
  version = '';
  g0Status = '';
  g4Status = '';
  g5Status = '';
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        commandsDisabled: boolean;
        sendEnabled: boolean;
        createsTaxCredit: boolean;
        g0Status: string;
        g4Status: string;
        g5Status: string;
        items: unknown[];
        queue: unknown[];
        disclaimer: string;
      }>('/v1/collection')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.g0Status = body.g0Status;
          this.g4Status = body.g4Status;
          this.g5Status = body.g5Status;
          const empty = body.items.length === 0 && body.queue.length === 0;
          this.state = empty ? 'empty' : 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o painel de cobrança.';
          this.state = 'error';
        },
      });
  }
}
