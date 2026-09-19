import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type NotificationsViewState = 'loading' | 'empty' | 'ok' | 'error';

@Component({
  selector: 'app-notifications-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications-page.component.html',
  styleUrl: './notifications-page.component.scss',
})
export class NotificationsPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: NotificationsViewState = 'loading';
  disclaimer = '';
  catalogVersion = '';
  g5Status = '';
  sendMessage = '';
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        catalogVersion: string;
        g5Status: string;
        items: unknown[];
        disclaimer: string;
        sendEnabled: boolean;
        commandsDisabled: boolean;
      }>('/v1/notifications')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.catalogVersion = body.catalogVersion;
          this.g5Status = body.g5Status;
          this.state = body.items.length ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar as notificações técnicas.';
          this.state = 'error';
        },
      });
  }

  attemptSend(): void {
    this.sendMessage = '';
    this.http.post('/v1/notifications', {}).subscribe({
      next: () => {
        this.sendMessage = 'Envio inesperadamente aceito.';
      },
      error: () => {
        this.sendMessage =
          'Envio recusado. Comandos desativados; nenhuma mensagem enviada.';
      },
    });
  }
}
