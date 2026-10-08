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
  styleUrl: '../tax-better/tax-better-page.scss',
})
export class LoginPageComponent {
  private readonly http = inject(HttpClient);
  private readonly session = inject(PublicOpenSessionService);
  private readonly router = inject(Router);
  username = '';
  password = '';
  code = '';
  message = '';
  submitting = false;

  submit(): void {
    this.submitting = true;
    this.message = '';
    this.http
      .post<LoginResponse>('/v1/auth/login', {
        username: this.username,
        password: this.password,
        code: this.code,
      })
      .subscribe({
        next: (body) => {
          this.password = '';
          this.code = '';
          this.session.rememberOperator({
            accessToken: body.accessToken,
            territoryId: body.territoryId,
            purposeId: body.purposeId,
            expiresAt: body.expiresAt,
            mode: body.mode,
            username: body.username,
          });
          this.submitting = false;
          void this.router.navigateByUrl('/administracao');
        },
        error: () => {
          this.password = '';
          this.code = '';
          this.message = 'Acesso não conferiu.';
          this.submitting = false;
        },
      });
  }
}
