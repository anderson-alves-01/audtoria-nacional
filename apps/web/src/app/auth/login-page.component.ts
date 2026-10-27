import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { PublicOpenSessionService } from '../auth/public-open-session.service';

interface LoginResponse {
  accessToken: string;
  expiresAt: string;
  territoryId: string;
  purposeId: string;
  mode: string;
  username: string;
  createsTaxCredit: boolean;
}

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login-page.component.html',
  styles: [
    `
      :host {
        display: grid;
        min-height: 100vh;
        place-items: center;
        padding: var(--sp-5);
        background:
          linear-gradient(var(--line) 1px, transparent 1px) 0 0 / 48px 48px,
          linear-gradient(90deg, var(--line) 1px, transparent 1px) 0 0 / 48px 48px,
          var(--bg);
        color: var(--text);
      }
      section {
        width: min(24rem, 100%);
        background: var(--surface);
        border: 1px solid var(--line-strong);
        border-radius: var(--r-lg);
        box-shadow: var(--shadow-2);
        padding: var(--sp-6);
      }
      .mark {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: grid;
        place-items: center;
        background: var(--accent);
        color: var(--on-accent);
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: var(--sp-4);
      }
      h1 {
        margin-bottom: var(--sp-5);
      }
      label {
        display: block;
        margin-bottom: var(--sp-4);
      }
      input {
        display: block;
        width: 100%;
        margin-top: var(--sp-1);
      }
      button[type='submit'] {
        width: 100%;
        min-height: 40px;
      }
      [role='alert'] {
        margin: var(--sp-4) 0 0;
        color: var(--danger);
      }
    `,
  ],
})
export class LoginPageComponent {
  private readonly http = inject(HttpClient);
  private readonly session = inject(PublicOpenSessionService);
  private readonly router = inject(Router);
  username = '';
  password = '';
  message = '';
  submitting = false;

  submit(): void {
    this.submitting = true;
    this.message = '';
    this.http
      .post<LoginResponse>('/v1/auth/login', {
        username: this.username,
        password: this.password,
      })
      .subscribe({
        next: (body) => {
          this.password = '';
          this.session.rememberOperator({
            accessToken: body.accessToken,
            territoryId: body.territoryId,
            purposeId: body.purposeId,
            expiresAt: body.expiresAt,
            mode: body.mode,
            username: body.username,
          });
          this.submitting = false;
          void this.router.navigateByUrl('/visao');
        },
        error: () => {
          this.password = '';
          this.message = 'Acesso não conferiu.';
          this.submitting = false;
        },
      });
  }
}
