import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

interface VisionSide {
  valor: string | null;
  baseCalculo: string | null;
  imposto: string | null;
}

interface VisionRow {
  imposto: string;
  fgo: string;
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
  imports: [CommonModule],
  templateUrl: './tax-better-vision-page.component.html',
  styleUrl: './tax-better-page.scss',
})
export class TaxBetterVisionPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: 'loading' | 'ok' | 'error' = 'loading';
  view: VisionView | null = null;
  errorMessage = '';

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

  variables(row: VisionRow): string {
    const pairs = Object.entries(row.variables || {});
    if (pairs.length === 0) {
      return '—';
    }
    return pairs.map(([key, value]) => `${key}: ${value}`).join('; ');
  }
}
