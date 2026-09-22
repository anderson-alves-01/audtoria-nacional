import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type AuditCasesViewState = 'loading' | 'empty' | 'ok' | 'error';

@Component({
  selector: 'app-audit-cases-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './audit-cases-page.component.html',
  styleUrl: './audit-cases-page.component.scss',
})
export class AuditCasesPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: AuditCasesViewState = 'loading';
  disclaimer = '';
  catalogVersion = '';
  g5Status = '';
  createMessage = '';
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        catalogVersion: string;
        g5Status: string;
        items: unknown[];
        disclaimer: string;
        commandsDisabled: boolean;
      }>('/v1/cases')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.catalogVersion = body.catalogVersion;
          this.g5Status = body.g5Status;
          this.state = body.items.length ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar os casos de auditoria.';
          this.state = 'error';
        },
      });
  }

  attemptCreate(): void {
    this.createMessage = '';
    this.http.post('/v1/cases', {}).subscribe({
      next: () => {
        this.createMessage = 'Criação inesperadamente aceita.';
      },
      error: () => {
        this.createMessage =
          'Criação recusada. Comandos desativados; nenhum registro persistido.';
      },
    });
  }
}
