import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { EvidenceDrawerComponent } from '../shared/evidence/evidence-drawer.component';
import { EmptyStateComponent } from '../shared/states/empty-state.component';
import { ErrorStateComponent } from '../shared/states/error-state.component';
import { SkeletonComponent } from '../shared/states/skeleton.component';
import { KpiCardComponent } from '../shared/ui/kpi-card.component';

export type SectoralEnrichmentViewState = 'loading' | 'empty' | 'ok' | 'error';

export interface SectoralSourceRow {
  sourceId: string;
  maintainer: string;
  status: string;
  ingestAllowed: boolean;
  structuredOfficialSource: string;
}

interface SectorTab {
  id: string;
  label: string;
}

const SECTORS: SectorTab[] = [
  { id: 'todos', label: 'Todos' },
  { id: 'combustiveis', label: 'Combustíveis' },
  { id: 'energia', label: 'Energia' },
  { id: 'telecom', label: 'Telecomunicações' },
  { id: 'financeiro', label: 'Financeiro' },
  { id: 'saude', label: 'Saúde' },
];

function sectorOf(sourceId: string): string {
  if (sourceId.startsWith('ANP')) {
    return 'combustiveis';
  }
  if (sourceId.startsWith('ANEEL') || sourceId.startsWith('EPE')) {
    return 'energia';
  }
  if (sourceId.startsWith('ANATEL')) {
    return 'telecom';
  }
  if (sourceId.startsWith('BCB')) {
    return 'financeiro';
  }
  if (sourceId.startsWith('CNES')) {
    return 'saude';
  }
  return 'todos';
}

@Component({
  selector: 'app-sectoral-enrichment-page',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    KpiCardComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    SkeletonComponent,
    EvidenceDrawerComponent,
  ],
  templateUrl: './sectoral-enrichment-page.component.html',
  styleUrl: './sectoral-enrichment-page.component.scss',
})
export class SectoralEnrichmentPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  readonly sectors = SECTORS;
  state: SectoralEnrichmentViewState = 'loading';
  disclaimer = '';
  version = '';
  ingestEnabled = false;
  createsTaxCredit = true;
  institutionalStatus = '';
  sources: SectoralSourceRow[] = [];
  errorMessage = '';
  correlationId = '';
  selectedSector = 'todos';
  sourceQuery = '';
  evidenceOpen = false;
  selected: SectoralSourceRow | null = null;

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.state = 'loading';
    this.http
      .get<{
        version: string;
        ingestEnabled: boolean;
        createsTaxCredit: boolean;
        institutionalStatus: string;
        sources: SectoralSourceRow[];
        items: unknown[];
        disclaimer: string;
      }>('/v1/sectoral-enrichment')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.ingestEnabled = body.ingestEnabled;
          this.createsTaxCredit = body.createsTaxCredit;
          this.institutionalStatus = body.institutionalStatus;
          this.sources = body.sources || [];
          this.state = (body.items || []).length === 0 ? 'empty' : 'ok';
        },
        error: (err: HttpErrorResponse) => {
          this.correlationId = err.headers?.get('x-trace-id') || '';
          this.errorMessage = 'Não foi possível carregar o enriquecimento setorial.';
          this.state = 'error';
        },
      });
  }

  get visibleSources(): SectoralSourceRow[] {
    return this.sources.filter((row) => {
      const sectorOk = this.selectedSector === 'todos' || sectorOf(row.sourceId) === this.selectedSector;
      const query = this.sourceQuery.trim().toLowerCase();
      const queryOk =
        !query ||
        row.sourceId.toLowerCase().includes(query) ||
        row.maintainer.toLowerCase().includes(query) ||
        row.status.toLowerCase().includes(query);
      return sectorOk && queryOk;
    });
  }

  get approvedCount(): number {
    return this.sources.filter((row) => row.status === 'TECHNICALLY_APPROVED').length;
  }

  sectorLabel(sourceId: string): string {
    return this.sectors.find((sector) => sector.id === sectorOf(sourceId))?.label || 'Outros';
  }

  openEvidence(row: SectoralSourceRow): void {
    this.selected = row;
    this.evidenceOpen = true;
  }
}
