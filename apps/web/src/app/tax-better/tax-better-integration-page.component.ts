import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface TaxBetterDraft {
  sourceId: string;
  channel: string;
  fieldMap: Record<string, string>;
  endpoint: string;
  secretName: string;
  createsTaxCredit: boolean;
}

@Component({
  selector: 'app-tax-better-integration-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './tax-better-integration-page.component.html',
  styleUrl: './tax-better-page.scss',
})
export class TaxBetterIntegrationPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  readonly sourceId = 'TAX-BETTER-ENTRADA';
  readonly intakeFields = [
    { key: 'organ', label: 'Órgão' },
    { key: 'tax', label: 'Imposto' },
    { key: 'fgo', label: 'Fato gerador' },
    { key: 'operationValue', label: 'Valor da operação' },
    { key: 'operationBase', label: 'Base da operação' },
    { key: 'operationTax', label: 'Imposto da operação' },
    { key: 'malhaValue', label: 'Valor da malha' },
    { key: 'malhaBase', label: 'Base da malha' },
    { key: 'malhaTax', label: 'Imposto da malha' },
  ];
  state: 'loading' | 'ok' | 'error' = 'loading';
  draft: TaxBetterDraft | null = null;
  competence = '';
  fileText = '';
  apiBody = '';
  message = '';

  ngOnInit(): void {
    this.http.get<Partial<TaxBetterDraft>>(`/v1/data-sources/${this.sourceId}/tax-better-config`).subscribe({
      next: (body) => {
        this.draft = this.mergeDraft(body);
        this.state = 'ok';
      },
      error: () => {
        this.message = 'A configuração de entrada não pôde ser lida.';
        this.state = 'error';
      },
    });
  }

  saveConfig(): void {
    if (!this.draft) {
      return;
    }
    this.message = '';
    this.http
      .put<TaxBetterDraft>(`/v1/data-sources/${this.sourceId}/tax-better-config`, {
        channel: this.draft.channel,
        fieldMap: this.draft.fieldMap,
        endpoint: this.draft.endpoint,
        secretName: this.draft.secretName,
      })
      .subscribe({
        next: (body) => {
          this.draft = this.mergeDraft(body);
          this.message = 'Mapa gravado. A busca ao órgão continua bloqueada. Nenhum crédito foi criado.';
        },
        error: () => {
          this.message = 'O mapa não foi gravado. Confira o canal, os campos e o nome do segredo.';
        },
      });
  }

  stageFile(): void {
    if (!this.draft || this.draft.channel !== 'file') {
      return;
    }
    this.postIntake({ fileText: this.fileText, competence: this.competence || null });
  }

  stageApi(): void {
    if (!this.draft || this.draft.channel !== 'api') {
      return;
    }
    let rows: unknown;
    try {
      rows = JSON.parse(this.apiBody || '[]');
    } catch {
      this.message = 'A resposta precisa ser uma lista JSON. Nenhuma busca ao órgão foi feita.';
      return;
    }
    if (!Array.isArray(rows)) {
      this.message = 'A resposta precisa ser uma lista JSON. Nenhuma busca ao órgão foi feita.';
      return;
    }
    this.postIntake({ rows, competence: this.competence || null });
  }

  private postIntake(body: { fileText?: string; rows?: unknown; competence: string | null }): void {
    this.message = '';
    this.http
      .post<{ createsTaxCredit: boolean; acceptedCount: number; quarantinedCount: number }>(
        `/v1/data-sources/${this.sourceId}/tax-better-intake`,
        body,
      )
      .subscribe({
        next: (result) => {
          const credit = result.createsTaxCredit ? 'sim' : 'não';
          this.message =
            `Linhas registradas. Aceitas: ${result.acceptedCount}. Quarentena: ${result.quarantinedCount}. Cria crédito: ${credit}.`;
        },
        error: () => {
          this.message = 'O registro foi recusado. Grave o leiaute e o nome do segredo antes.';
        },
      });
  }

  private mergeDraft(body: Partial<TaxBetterDraft>): TaxBetterDraft {
    const fieldMap: Record<string, string> = {};
    for (const field of this.intakeFields) {
      fieldMap[field.key] = body.fieldMap?.[field.key] || '';
    }
    return {
      sourceId: this.sourceId,
      channel: body.channel || 'file',
      fieldMap,
      endpoint: body.endpoint || '',
      secretName: body.secretName || '',
      createsTaxCredit: false,
    };
  }
}
