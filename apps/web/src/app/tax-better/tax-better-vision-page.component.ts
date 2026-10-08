import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { EChartsOption } from 'echarts';
import { NgxEchartsDirective, provideEcharts } from 'ngx-echarts';
import { buildChartOptions } from '../shared/charts/chart-options';
import { EmptyStateComponent } from '../shared/states/empty-state.component';
import { KpiCardComponent } from '../shared/ui/kpi-card.component';

interface VisionSide {
  valor: string | null;
  baseCalculo: string | null;
  imposto: string | null;
}

interface VisionRow {
  orgao?: string;
  imposto: string;
  fgo: string;
  periodo?: string | null;
  variables: Record<string, string>;
  operacao: VisionSide;
  malha: VisionSide;
  approved: boolean;
}

interface VisionView {
  createsTaxCredit: boolean;
  approvedExport: boolean;
  emptyReason: string | null;
  rows: VisionRow[];
}

@Component({
  selector: 'app-tax-better-vision-page',
  standalone: true,
  imports: [CommonModule, FormsModule, NgxEchartsDirective, KpiCardComponent, EmptyStateComponent],
  providers: [provideEcharts()],
  templateUrl: './tax-better-vision-page.component.html',
  styleUrl: './tax-better-page.scss',
})
export class TaxBetterVisionPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: 'loading' | 'ok' | 'error' = 'loading';
  view: VisionView | null = null;
  errorMessage = '';
  filterImposto = '';
  filterFgo = '';
  filterOrgao = '';
  filterPeriodo = '';
  filterVariavel = '';

  ngOnInit(): void {
    this.http.get<VisionView>('/v1/tax-better/vision').subscribe({
      next: (body) => {
        this.view = {
          createsTaxCredit: false,
          approvedExport: false,
          emptyReason: body.emptyReason,
          rows: body.rows || [],
        };
        this.state = 'ok';
      },
      error: () => {
        this.errorMessage = 'A visão não pôde ser lida.';
        this.state = 'error';
      },
    });
  }

  options(field: 'imposto' | 'fgo' | 'orgao' | 'periodo'): string[] {
    const values = new Set<string>();
    for (const row of this.view?.rows || []) {
      const value = this.fieldValue(row, field);
      if (value) {
        values.add(value);
      }
    }
    return [...values].sort((left, right) => left.localeCompare(right, 'pt-BR'));
  }

  get filtered(): VisionRow[] {
    const term = this.filterVariavel.trim().toLowerCase();
    return (this.view?.rows || []).filter((row) => {
      if (this.filterImposto && row.imposto !== this.filterImposto) {
        return false;
      }
      if (this.filterFgo && row.fgo !== this.filterFgo) {
        return false;
      }
      if (this.filterOrgao && (row.orgao || '') !== this.filterOrgao) {
        return false;
      }
      if (this.filterPeriodo && (row.periodo || '') !== this.filterPeriodo) {
        return false;
      }
      if (!term) {
        return true;
      }
      return this.variables(row).toLowerCase().includes(term);
    });
  }

  get approvedCount(): number {
    return this.filtered.filter((row) => row.approved).length;
  }

  operationChart(): EChartsOption | null {
    return this.chart('operacao', 'valor', 'imposto', 'Valor da operação');
  }

  malhaChart(): EChartsOption | null {
    return this.chart('malha', 'valor', 'fgo', 'Valor da malha');
  }

  measure(value: string | null | undefined): string {
    if (value === null || value === undefined || value === '') {
      return '—';
    }
    const number = Number(value);
    if (Number.isNaN(number)) {
      return value;
    }
    return number.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 4 });
  }

  sum(side: 'operacao' | 'malha', field: keyof VisionSide): string {
    let total = 0;
    let seen = false;
    for (const row of this.filtered) {
      const raw = row[side][field];
      if (raw === null || raw === undefined || raw === '') {
        continue;
      }
      const number = Number(raw);
      if (Number.isNaN(number)) {
        continue;
      }
      total += number;
      seen = true;
    }
    return seen ? this.measure(String(total)) : '—';
  }

  variables(row: VisionRow): string {
    const pairs = Object.entries(row.variables || {});
    if (pairs.length === 0) {
      return '—';
    }
    return pairs.map(([key, value]) => `${key}: ${value}`).join('; ');
  }

  private fieldValue(row: VisionRow, field: 'imposto' | 'fgo' | 'orgao' | 'periodo'): string {
    if (field === 'orgao') {
      return row.orgao || '';
    }
    if (field === 'periodo') {
      return row.periodo || '';
    }
    return row[field] || '';
  }

  private chart(
    side: 'operacao' | 'malha',
    field: keyof VisionSide,
    group: 'imposto' | 'fgo',
    seriesName: string,
  ): EChartsOption | null {
    const totals = new Map<string, number>();
    for (const row of this.filtered) {
      const raw = row[side][field];
      if (raw === null || raw === undefined || raw === '') {
        continue;
      }
      const number = Number(raw);
      if (Number.isNaN(number)) {
        continue;
      }
      const label = row[group];
      totals.set(label, (totals.get(label) || 0) + number);
    }
    const points = [...totals.entries()].map(([x, y]) => ({ x, y }));
    if (points.length === 0) {
      return null;
    }
    return buildChartOptions({ chartType: 'bar', seriesName, points, unit: 'BRL' });
  }
}
