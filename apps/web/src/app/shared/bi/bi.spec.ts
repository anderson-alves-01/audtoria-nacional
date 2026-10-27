import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import {
  BiChartInput,
  alternativeHeaders,
  alternativeRows,
  alternativeUnits,
  buildBiOptions,
  toIndexValues,
} from './bi-chart-options';
import { SavedViews, compareSeries } from './bi-extras';
import { BiFilters } from './bi-filters';
import { DataTableComponent } from './data-table.component';
import { BiColumn, filterRows, groupRows, sortRows, toCsv } from './table-logic';

interface Row {
  imposto: string;
  valor: number | null;
}

const columns: BiColumn<Row>[] = [
  { id: 'imposto', label: 'Imposto', value: (row) => row.imposto },
  { id: 'valor', label: 'Valor', value: (row) => row.valor, numeric: true },
];

const rows: Row[] = [
  { imposto: 'ICMS', valor: 10 },
  { imposto: 'ISS', valor: null },
  { imposto: 'ICMS', valor: 5 },
  { imposto: 'IPVA', valor: 7 },
];

describe('table logic', () => {
  it('sorts numbers and always keeps empty values last', () => {
    const asc = sortRows(rows, columns, { column: 'valor', direction: 'asc' }).map((r) => r.valor);
    const desc = sortRows(rows, columns, { column: 'valor', direction: 'desc' }).map((r) => r.valor);
    expect(asc).toEqual([5, 7, 10, null]);
    expect(desc).toEqual([10, 7, 5, null]);
  });

  it('filters by what is shown in the column', () => {
    expect(filterRows(rows, columns, { imposto: 'ic' }).length).toBe(2);
    expect(filterRows(rows, columns, { valor: '—' }).length).toBe(1);
  });

  it('groups and sums only existing values, never turning empty into zero', () => {
    const groups = groupRows(rows, columns, 'imposto');
    const icms = groups.find((g) => g.key === 'ICMS');
    const iss = groups.find((g) => g.key === 'ISS');
    expect(icms?.sums['valor']).toBe(15);
    expect(iss?.sums['valor']).toBeNull();
    expect(iss?.count).toBe(1);
  });

  it('exports what is on screen with a dash for empty cells', () => {
    const csv = toCsv(rows.slice(0, 2), columns);
    expect(csv).toContain('Imposto;Valor');
    expect(csv).toContain('ISS;—');
  });
});

describe('bi filters', () => {
  it('cross-filters by dimension and keeps the others in the match', () => {
    const filters = new BiFilters(['imposto', 'fgo']);
    filters.toggle('imposto', 'ICMS');
    expect(filters.matches({ imposto: 'ICMS', fgo: 'a' })).toBeTrue();
    expect(filters.matches({ imposto: 'ISS', fgo: 'a' })).toBeFalse();
    expect(filters.matches({ imposto: 'ISS' }, 'imposto')).toBeTrue();
  });

  it('drills down level by level and goes back up', () => {
    const filters = new BiFilters(['imposto', 'fgo']);
    expect(filters.currentLevel).toBe('imposto');
    filters.drillInto('ICMS');
    expect(filters.currentLevel).toBe('fgo');
    expect(filters.matches({ imposto: 'ICMS', fgo: 'x' })).toBeTrue();
    expect(filters.matches({ imposto: 'ISS', fgo: 'x' })).toBeFalse();
    filters.drillUp();
    expect(filters.currentLevel).toBe('imposto');
  });

  it('round-trips through the url parameters', () => {
    const filters = new BiFilters(['imposto', 'fgo']);
    filters.toggle('orgao', 'DETRAN', true);
    filters.toggle('orgao', 'SEFAZ', true);
    filters.drillInto('ICMS');
    const params = filters.toParams();
    expect(params['f.orgao']).toBe('DETRAN~SEFAZ');
    expect(params['drill']).toBe('ICMS');
    const other = new BiFilters(['imposto', 'fgo']);
    other.load((key) => params[key] ?? null, Object.keys(params));
    expect(other.selections()['orgao']).toEqual(['DETRAN', 'SEFAZ']);
    expect(other.drillPath()).toEqual(['ICMS']);
  });

  it('builds readable chips without raw keys', () => {
    const filters = new BiFilters(['imposto']);
    filters.toggle('orgao', 'DETRAN');
    const chips = filters.chips({ orgao: 'Órgão' });
    expect(chips[0]).toEqual({ key: 'orgao', label: 'Órgão', value: 'DETRAN' });
  });
});

describe('bi extras', () => {
  it('compares two competences without turning a missing side into zero', () => {
    const result = compareSeries(
      ['ICMS', 'ISS', 'IPVA'],
      new Map<string, number | null>([['ICMS', 150], ['ISS', 10]]),
      new Map<string, number | null>([['ICMS', 100], ['IPVA', 0]]),
    );
    expect(result[0]).toEqual({ category: 'ICMS', current: 150, previous: 100, delta: 50, deltaPct: 50 });
    expect(result[1].delta).toBeNull();
    expect(result[2].deltaPct).toBeNull();
  });

  it('saves and removes views by name in the browser', () => {
    localStorage.removeItem('sirta.views.teste');
    const views = new SavedViews('teste');
    views.save('Só ICMS', { 'f.imposto': 'ICMS' });
    views.save('Só ICMS', { 'f.imposto': 'ICMS~ISS' });
    expect(views.list().length).toBe(1);
    expect(views.list()[0].params['f.imposto']).toBe('ICMS~ISS');
    views.remove('Só ICMS');
    expect(views.list()).toEqual([]);
  });
});

describe('bi chart options', () => {
  const input: BiChartInput = {
    kind: 'bar',
    unit: 'BRL',
    categories: ['ICMS', 'ISS'],
    series: [{ name: 'Operação', values: [10, null] }],
    selected: ['ICMS'],
  };

  it('dims the categories outside the selection and keeps null as a gap', () => {
    const options = buildBiOptions(input);
    const series = options.series as { data: { value: number | null; itemStyle: { opacity?: number } }[] }[];
    expect(series[0].data[0].itemStyle.opacity).toBeUndefined();
    expect(series[0].data[1].itemStyle.opacity).toBe(0.3);
    expect(series[0].data[1].value).toBeNull();
  });

  it('always offers an alternative table', () => {
    expect(alternativeHeaders(input)).toEqual(['Operação']);
    expect(alternativeRows(input)).toEqual([
      { label: 'ICMS', values: [10] },
      { label: 'ISS', values: [null] },
    ]);
    const heat: BiChartInput = {
      kind: 'heatmap',
      unit: 'BRL',
      categories: ['2025'],
      rowLabels: ['ICMS'],
      cells: [[0, 0, 3]],
    };
    expect(alternativeRows(heat)).toEqual([{ label: 'ICMS', values: [3] }]);
  });

  it('puts a series on a secondary right axis with its own unit', () => {
    const dual: BiChartInput = {
      kind: 'line',
      unit: 'COUNT',
      categories: ['2021', '2022'],
      series: [
        { name: 'Quantidade', values: [10, 20] },
        { name: 'Valor estimado', values: [1000, null], axis: 'right', unit: 'BRL' },
      ],
    };
    const options = buildBiOptions(dual);
    const yAxis = options.yAxis as { position?: string; splitLine?: { show?: boolean } }[];
    expect(Array.isArray(yAxis)).toBeTrue();
    expect(yAxis.length).toBe(2);
    expect(yAxis[1].position).toBe('right');
    expect(yAxis[1].splitLine?.show).toBeFalse();
    const series = options.series as { yAxisIndex: number; data: { value: number | null }[] }[];
    expect(series.map((entry) => entry.yAxisIndex)).toEqual([0, 1]);
    expect(series[1].data[1].value).toBeNull();
    expect(alternativeUnits(dual)).toEqual(['COUNT', 'BRL']);
  });

  it('pairs a dashed series with the colour of its public counterpart', () => {
    const options = buildBiOptions({
      kind: 'line',
      unit: 'COUNT',
      categories: ['a', 'b'],
      series: [
        { name: 'Publico', values: [1, null] },
        { name: 'Outro', values: [2, null] },
        { name: 'Simulado', values: [null, 3], dashed: true, colorLike: 'Publico' },
      ],
    });
    const series = options.series as { color: string; lineStyle: { type: string } }[];
    expect(series[2].color).toBe(series[0].color);
    expect(series[2].color).not.toBe(series[1].color);
    expect(series[2].lineStyle.type).toBe('dashed');
    expect(series[0].lineStyle.type).toBe('solid');
  });

  it('keeps a single axis when no series asks for the right one', () => {
    const options = buildBiOptions(input);
    expect(Array.isArray(options.yAxis)).toBeFalse();
  });

  it('rebases a series to 100 at the first existing value and keeps gaps', () => {
    expect(toIndexValues([null, 50, 100, 25])).toEqual([null, 100, 200, 50]);
    expect(toIndexValues([0, 10])).toEqual([null, null]);
    expect(toIndexValues([null, null])).toEqual([null, null]);
  });

  it('builds every chart kind without throwing', () => {
    for (const kind of ['bar', 'barH', 'line', 'area', 'scatter', 'treemap', 'funnel', 'heatmap'] as const) {
      const options = buildBiOptions({
        kind,
        unit: 'COUNT',
        categories: ['a'],
        series: [{ name: 's', values: [1] }],
        points: [{ name: 'p', x: 1, y: 2 }],
        items: [{ name: 'i', value: 3 }],
        rowLabels: ['r'],
        cells: [[0, 0, 1]],
      });
      expect(options.series).toBeTruthy();
    }
  });
});

@Component({
  standalone: true,
  imports: [DataTableComponent],
  template: `<app-data-table [columns]="columns" [rows]="rows" [rowKey]="key" />`,
})
class TableHostComponent {
  columns = columns;
  rows = rows;
  key = (row: Row): string => row.imposto + row.valor;
}

describe('data table', () => {
  it('shows the row count and an accessible table with sortable headers', () => {
    const fixture = TestBed.createComponent(TableHostComponent);
    fixture.detectChanges();
    const root = fixture.nativeElement as HTMLElement;
    expect(root.querySelector('[role=table]')).not.toBeNull();
    expect(root.querySelector('.dt-count')?.textContent).toContain('4 de 4 linhas');
    const headers = root.querySelectorAll('[role=columnheader][aria-sort]');
    expect(headers.length).toBe(2);
  });

  it('filters rows from the column filter field', () => {
    const fixture = TestBed.createComponent(TableHostComponent);
    fixture.detectChanges();
    const root = fixture.nativeElement as HTMLElement;
    const field = root.querySelector('input[aria-label="Filtrar Imposto"]') as HTMLInputElement;
    field.value = 'ICMS';
    field.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    expect(root.querySelector('.dt-count')?.textContent).toContain('2 de 4 linhas');
  });
});
