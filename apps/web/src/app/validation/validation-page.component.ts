import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

export type ValidationViewState = 'idle' | 'loading' | 'ok' | 'error' | 'forbidden';

export const CREDIT_LEGALITY_ITEMS = [
  { code: 'ORIGIN_IDENTIFIED', label: 'Origem oficial identificada' },
  { code: 'TAX_COMPETENCE_CONFIRMED', label: 'Tributo e competência confirmados' },
  { code: 'TAXPAYER_LINKED', label: 'Contribuinte corretamente vinculado' },
  { code: 'FACT_AND_LEGAL_BASIS', label: 'Fato e fundamento registrados' },
  { code: 'PRINCIPAL_AND_ADDITIONS', label: 'Principal e acréscimos discriminados' },
  { code: 'CALCULATION_MEMORY', label: 'Memória de cálculo anexada' },
  { code: 'PAYMENTS_RECONCILED', label: 'Pagamentos e compensações conciliados' },
  { code: 'DUPLICITY_DISCARDED', label: 'Duplicidade descartada' },
  { code: 'ENFORCEABILITY_CHECKED', label: 'Exigibilidade verificada' },
  { code: 'SUSPENSION_EXTINCTION_BLOCK', label: 'Suspensão, extinção ou impedimento verificados' },
  { code: 'DEADLINES_REVIEWED', label: 'Prazos relevantes analisados' },
  { code: 'EVIDENCE_HASHED', label: 'Evidências íntegras e com hash' },
  { code: 'CONTRADICTION_PRESERVED', label: 'Contraditório e defesa preservados' },
  { code: 'OPINION_RECORDED', label: 'Parecer e decisão registrados' },
  { code: 'VALIDATOR_AUTHORIZED', label: 'Usuário validador autorizado' },
] as const;

@Component({
  selector: 'app-validation-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './validation-page.component.html',
  styleUrl: './validation-page.component.scss',
})
export class ValidationPageComponent {
  private readonly http = inject(HttpClient);

  state: ValidationViewState = 'idle';
  creditId = '';
  evidenceId = '';
  territoryId = '';
  purposeId = '';
  accessToken = '';
  decision = 'APPROVE';
  rationale = '';
  errorMessage = '';
  validationStatus = '';
  items = CREDIT_LEGALITY_ITEMS.map((item) => ({ ...item, satisfied: false }));

  submit(): void {
    if (!this.creditId || !this.evidenceId) {
      this.state = 'error';
      this.errorMessage = 'Informe o crédito e ao menos uma evidência sintética.';
      return;
    }
    this.state = 'loading';
    this.errorMessage = '';
    const headers = new HttpHeaders({
      Authorization: `Bearer ${this.accessToken}`,
      'X-Territory-Id': this.territoryId,
      'X-Purpose-Id': this.purposeId,
      'Idempotency-Key': `ui-${crypto.randomUUID()}`,
    });
    this.http
      .post<{ validationStatus: string }>(`/v1/tax-credits/${this.creditId}/validations`, {
        decision: this.decision,
        checklistVersion: 'credit-legality-v1',
        evidenceIds: [this.evidenceId],
        rationale: this.rationale,
        checklistItems: this.items.map((item) => ({
          code: item.code,
          satisfied: item.satisfied,
        })),
      }, { headers })
      .subscribe({
        next: (body) => {
          this.validationStatus = body.validationStatus;
          this.state = 'ok';
        },
        error: (err: HttpErrorResponse) => {
          if (err.status === 403) {
            this.state = 'forbidden';
            this.errorMessage = 'A API recusou a validação para este papel ou contexto.';
            return;
          }
          this.state = 'error';
          this.errorMessage =
            err.status === 409
              ? 'Transição inválida. O crédito não foi alterado.'
              : 'Não foi possível registrar a validação.';
        },
      });
  }
}
