import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  humanizeCatalogToken,
  humanizeHomologation,
  humanizeQuality,
  humanizeSource,
} from '../shared/presentation/official-labels';

interface SourceItem {
  sourceId: string;
  name: string;
  sourceRole: string;
  accessClassification: string;
  status: string;
  ingestAllowed: boolean;
  createsTaxCredit: boolean;
  fixtureKind?: string;
  connector?: string;
}

interface EnrichmentView {
  sourceId: string;
  sourceRole?: string;
  published: boolean;
  indicatorCount: number;
  createsTaxCredit: boolean;
  banner?: string;
  homologationStatus?: string;
  emptyReason?: string;
  officialUrl?: string;
  competence?: string;
  formula?: string;
  methodologyVersion?: string;
  qualityLevel?: string;
  quarantinedCount?: number;
  note?: string;
}

interface TaxBetterDraft {
  sourceId: string;
  channel: string;
  fieldMap: Record<string, string>;
  endpoint: string;
  secretName: string;
  createsTaxCredit: boolean;
}

@Component({
  selector: 'app-sources-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './sources-page.component.html',
  styleUrl: './sources-page.component.scss',
})
export class SourcesPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: 'loading' | 'ok' | 'error' = 'loading';
  items: SourceItem[] = [];
  enrichment: EnrichmentView | null = null;
  ingestMessage = '';
  configMessage = '';
  errorMessage = '';
  draft: TaxBetterDraft | null = null;
  fileText = '';
  apiBody = '';
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
  readonly banner =
    'DADOS DE FONTE OFICIAL — PROCESSAMENTO TÉCNICO CONCLUÍDO — HOMOLOGAÇÃO HUMANA PENDENTE';

  sourceHeading(sourceId: string): string {
    return humanizeSource(sourceId);
  }

  catalogText(code: string | null | undefined): string {
    return humanizeCatalogToken(code);
  }

  qualityText(level: string | null | undefined): string {
    return humanizeQuality(level);
  }

  validationText(status: string | null | undefined): string {
    return humanizeHomologation(status);
  }

  isTaxBetter(item: SourceItem): boolean {
    return item.connector === 'tax_better_intake';
  }

  ngOnInit(): void {
    this.http.get<{ items: SourceItem[] }>('/v1/data-sources').subscribe({
      next: (body) => {
        this.items = body.items;
        this.state = 'ok';
        this.loadEnrichment('IBGE-SIDRA');
        const configured = this.items.find((item) => this.isTaxBetter(item));
        if (configured) {
          this.loadConfig(configured);
        }
      },
      error: () => {
        this.errorMessage = 'Não foi possível carregar o catálogo oficial de fontes.';
        this.state = 'error';
      },
    });
  }

  ingest(item: SourceItem): void {
    this.ingestMessage = '';
    this.http.post(`/v1/data-sources/${item.sourceId}/ingest`, {}).subscribe({
      next: () => {
        this.ingestMessage = `Fonte oficial ${item.sourceId} ingerida. Nenhum crédito tributário foi criado.`;
        this.loadEnrichment(item.sourceId);
      },
      error: () => {
        this.ingestMessage = `Ingestão recusada ou indisponível para ${item.sourceId}.`;
      },
    });
  }

  saveConfig(): void {
    if (!this.draft) {
      return;
    }
    const sourceId = this.draft.sourceId;
    this.configMessage = '';
    this.http
      .put<TaxBetterDraft>(`/v1/data-sources/${sourceId}/tax-better-config`, {
        channel: this.draft.channel,
        fieldMap: this.draft.fieldMap,
        endpoint: this.draft.endpoint,
        secretName: this.draft.secretName,
      })
      .subscribe({
        next: (body) => {
          this.draft = this.mergeDraft(sourceId, body);
          this.configMessage =
            'Mapa gravado. A busca ao órgão continua bloqueada. Nenhum crédito foi criado.';
        },
        error: () => {
          this.configMessage =
            'O mapa não foi gravado. Confira o canal, os campos e o nome do segredo.';
        },
      });
  }

  stageFile(): void {
    if (!this.draft || this.draft.channel !== 'file') {
      return;
    }
    const sourceId = this.draft.sourceId;
    this.configMessage = '';
    this.http
      .post<{ createsTaxCredit: boolean; acceptedCount: number; quarantinedCount: number }>(
        `/v1/data-sources/${sourceId}/tax-better-intake`,
        { fileText: this.fileText },
      )
      .subscribe({
        next: (body) => {
          const credit = body.createsTaxCredit ? 'sim' : 'não';
          this.configMessage =
            `Arquivo lido. Aceitas: ${body.acceptedCount}. Quarentena: ${body.quarantinedCount}. Cria crédito: ${credit}.`;
        },
        error: () => {
          this.configMessage = 'Arquivo recusado. Grave o leiaute antes de enviar as linhas.';
        },
      });
  }

  stageApi(): void {
    if (!this.draft || this.draft.channel !== 'api') {
      return;
    }
    let rows: unknown;
    try {
      rows = JSON.parse(this.apiBody || '[]');
    } catch {
      this.configMessage = 'A resposta precisa ser uma lista JSON. Nenhuma busca ao órgão foi feita.';
      return;
    }
    if (!Array.isArray(rows)) {
      this.configMessage = 'A resposta precisa ser uma lista JSON. Nenhuma busca ao órgão foi feita.';
      return;
    }
    const sourceId = this.draft.sourceId;
    this.configMessage = '';
    this.http
      .post<{ createsTaxCredit: boolean; acceptedCount: number; quarantinedCount: number }>(
        `/v1/data-sources/${sourceId}/tax-better-intake`,
        { rows },
      )
      .subscribe({
        next: (body) => {
          const credit = body.createsTaxCredit ? 'sim' : 'não';
          this.configMessage =
            `Resposta lida. Aceitas: ${body.acceptedCount}. Quarentena: ${body.quarantinedCount}. Cria crédito: ${credit}.`;
        },
        error: () => {
          this.configMessage = 'Resposta recusada. Grave o mapa e o nome do segredo antes.';
        },
      });
  }

  private loadConfig(item: SourceItem): void {
    this.http
      .get<Partial<TaxBetterDraft>>(`/v1/data-sources/${item.sourceId}/tax-better-config`)
      .subscribe({
        next: (body) => {
          this.draft = this.mergeDraft(item.sourceId, body);
        },
        error: () => {
          this.draft = this.mergeDraft(item.sourceId, {});
          this.configMessage = 'A configuração desta fonte não pôde ser lida.';
        },
      });
  }

  private mergeDraft(sourceId: string, body: Partial<TaxBetterDraft>): TaxBetterDraft {
    const fieldMap: Record<string, string> = {};
    for (const field of this.intakeFields) {
      fieldMap[field.key] = body.fieldMap?.[field.key] || '';
    }
    return {
      sourceId,
      channel: body.channel || 'file',
      fieldMap,
      endpoint: body.endpoint || '',
      secretName: body.secretName || '',
      createsTaxCredit: false,
    };
  }

  private loadEnrichment(sourceId: string): void {
    this.http
      .get<EnrichmentView>('/v1/indicators/source-enrichment', { params: { sourceId } })
      .subscribe({
        next: (body) => {
          this.enrichment = body;
        },
        error: () => {
          this.enrichment = null;
        },
      });
  }
}
