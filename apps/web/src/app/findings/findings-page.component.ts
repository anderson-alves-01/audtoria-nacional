import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type FindingsViewState = 'loading' | 'empty' | 'ok' | 'error';

@Component({
  selector: 'app-findings-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './findings-page.component.html',
  styleUrl: './findings-page.component.scss',
})
export class FindingsPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: FindingsViewState = 'loading';
  disclaimer = '';
  catalogVersion = '';
  g5Status = '';
  total = 0;
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        catalogVersion: string;
        binding: boolean;
        operational: boolean;
        homologated: boolean;
        commandsDisabled: boolean;
        createsTaxCredit: boolean;
        legalCommandsEnabled: boolean;
        g5Status: string;
        items: unknown[];
        total: number;
        disclaimer: string;
      }>('/v1/findings')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.catalogVersion = body.catalogVersion;
          this.g5Status = body.g5Status;
          this.total = body.total;
          this.state = body.items.length ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar os achados técnicos.';
          this.state = 'error';
        },
      });
  }
}
