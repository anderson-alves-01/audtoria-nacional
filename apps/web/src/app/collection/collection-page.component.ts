import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

export type CollectionViewState = 'idle' | 'loading' | 'ok' | 'error' | 'forbidden';

@Component({
  selector: 'app-collection-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './collection-page.component.html',
  styleUrl: './collection-page.component.scss',
})
export class CollectionPageComponent {
  private readonly http = inject(HttpClient);
  state: CollectionViewState = 'idle';
  creditId = '';
  territoryId = '';
  purposeId = '';
  accessToken = '';
  errorMessage = '';
  collectionStatus = '';

  submit(): void {
    if (!this.creditId) {
      this.state = 'error';
      this.errorMessage = 'Informe o crédito validado.';
      return;
    }
    this.state = 'loading';
    const headers = new HttpHeaders({
      Authorization: `Bearer ${this.accessToken}`,
      'X-Territory-Id': this.territoryId,
      'X-Purpose-Id': this.purposeId,
      'Idempotency-Key': `ui-${crypto.randomUUID()}`,
    });
    this.http
      .post<{ collectionStatus: string }>(
        `/v1/tax-credits/${this.creditId}/collection-cases`,
        {},
        { headers },
      )
      .subscribe({
        next: (body) => {
          this.collectionStatus = body.collectionStatus;
          this.state = 'ok';
        },
        error: (err: HttpErrorResponse) => {
          if (err.status === 403) {
            this.state = 'forbidden';
            this.errorMessage = 'A API recusou a cobrança para este papel ou contexto.';
            return;
          }
          this.state = 'error';
          this.errorMessage =
            err.status === 409
              ? 'Cobrança bloqueada. O crédito não foi alterado.'
              : 'Não foi possível iniciar a cobrança.';
        },
      });
  }
}
