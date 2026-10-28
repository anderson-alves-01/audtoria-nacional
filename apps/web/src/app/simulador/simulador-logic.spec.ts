import { SpedSerieItem } from '../sped-operacoes/sped-logic';
import { GOODS_TYPES, ICMS_RATE_BY_UF, TAXES, rateFor } from './simulador-aliquotas';
import {
  allowedParam,
  publicByYear,
  referenceYear,
  sanitize,
  scenarioComparison,
  simulatorChart,
  taxAmount,
  taxByYear,
} from './simulador-logic';
import { HEX_LAYOUT } from '../atlas/hex-layout';

const items: SpedSerieItem[] = [
  { ano: 2021, uf: 'SP', operacao: 'Vendas', quantidade: 100, valorEstimado: '1000.00' },
  { ano: 2022, uf: 'SP', operacao: 'Vendas', quantidade: 200, valorEstimado: null },
  { ano: 2022, uf: 'SP', operacao: 'Compras', quantidade: 999, valorEstimado: '9999.00' },
  { ano: 2021, uf: 'AC', operacao: 'Vendas', quantidade: 10, valorEstimado: '50.00' },
];

describe('simulador aliquotas', () => {
  it('uses the fixed rates from the requirement', () => {
    expect(rateFor('ITCD', null)).toBe(6);
    expect(rateFor('ITBI', 'SP')).toBe(3);
    expect(rateFor('ISS', null)).toBe(5);
  });

  it('has an ICMS rate for each of the 27 UFs and fails closed for the rest', () => {
    expect(Object.keys(ICMS_RATE_BY_UF).sort()).toEqual(HEX_LAYOUT.map((cell) => cell.uf).sort());
    expect(rateFor('ICMS', 'SP')).toBe(18);
    expect(rateFor('ICMS', 'MA')).toBe(23);
    expect(rateFor('ICMS', 'PI')).toBe(22.5);
    expect(rateFor('ICMS', null)).toBeNull();
    expect(rateFor('ICMS', 'XX')).toBeNull();
  });

  it('lists the taxes and the goods types of the requirement', () => {
    expect(TAXES.map((tax) => tax.id)).toEqual(['ITCD', 'ITBI', 'ISS', 'ICMS']);
    expect(GOODS_TYPES.length).toBe(6);
  });
});

describe('simulador logic', () => {
  it('multiplies value by rate to the cent and keeps missing as null', () => {
    expect(taxAmount(1000, 6)).toBe(60);
    expect(taxAmount(100.5, 19.5)).toBe(19.6);
    expect(taxAmount(null, 6)).toBeNull();
    expect(taxAmount(1000, null)).toBeNull();
    expect(taxAmount(0, 6)).toBe(0);
  });

  it('accepts only finite non-negative numbers', () => {
    expect(sanitize(10)).toBe(10);
    expect(sanitize(0)).toBe(0);
    expect(sanitize(-1)).toBeNull();
    expect(sanitize(NaN)).toBeNull();
    expect(sanitize(null)).toBeNull();
  });

  it('reads one operation only and leaves a year without value empty', () => {
    const rows = publicByYear(items, [2021, 2022, 2023], 'Vendas', 'SP');
    expect(rows).toEqual([
      { year: 2021, quantity: 100, value: 1000 },
      { year: 2022, quantity: 200, value: null },
      { year: 2023, quantity: null, value: null },
    ]);
    expect(taxByYear(rows, 'ITCD', 'SP')).toEqual([60, null, null]);
    expect(taxByYear(rows, 'ICMS', null)).toEqual([null, null, null]);
  });

  it('compares the scenario with the public year and the tax difference', () => {
    const rows = publicByYear(items, [2021], 'Vendas', 'SP');
    const table = scenarioComparison(referenceYear(rows, 2021), { quantity: 150, value: 2000 }, ['ITCD', 'ICMS'], 'SP');
    expect(table.map((row) => row.label)).toEqual(['Quantidade', 'Valor', 'ITCD 6%', 'ICMS 18%']);
    expect(table[0].difference).toBe(50);
    expect(table[0].differencePercent).toBe(50);
    expect(table[1].difference).toBe(1000);
    expect(table[2].publicValue).toBe(60);
    expect(table[2].simulated).toBe(120);
    expect(table[2].difference).toBe(60);
    expect(table[3].simulated).toBe(360);
  });

  it('does not invent a difference when the public side is missing', () => {
    const rows = publicByYear(items, [2022], 'Vendas', 'SP');
    const table = scenarioComparison(referenceYear(rows, 2022), { quantity: 5, value: 100 }, ['ISS'], 'SP');
    expect(table[1].publicValue).toBeNull();
    expect(table[1].difference).toBeNull();
    expect(table[1].differencePercent).toBeNull();
    expect(table[2].difference).toBeNull();
    const none = scenarioComparison(null, { quantity: null, value: null }, ['ISS'], null);
    expect(none.every((row) => row.simulated === null && row.difference === null)).toBeTrue();
  });

  it('accepts a URL parameter only when it is in the known list', () => {
    expect(allowedParam('SP', ['AC', 'SP'], '')).toBe('SP');
    expect(allowedParam('XX', ['AC', 'SP'], '')).toBe('');
    expect(allowedParam(null, ['Vendas'], 'Vendas')).toBe('Vendas');
    expect(allowedParam('<script>', ['Vendas'], 'Vendas')).toBe('Vendas');
  });

  it('falls back to the latest year when the reference year is unknown', () => {
    const rows = publicByYear(items, [2021, 2022], 'Vendas', 'SP');
    expect(referenceYear(rows, 1999)?.year).toBe(2022);
    expect(referenceYear([], 2021)).toBeNull();
  });

  it('builds the chart with all public data and adds the simulated category', () => {
    const rows = publicByYear(items, [2021, 2022], 'Vendas', 'SP');
    const plain = simulatorChart(rows, ['ITCD'], 'SP', null);
    expect(plain.categories).toEqual(['2021', '2022']);
    expect(plain.series?.map((entry) => entry.name)).toEqual([
      'Quantidade',
      'Valor',
      'ITCD apurado',
    ]);
    expect(plain.series?.[1].axis).toBe('right');

    const chart = simulatorChart(rows, ['ITCD'], 'SP', { quantity: 150, value: 2000 });
    expect(chart.categories).toEqual(['2021', '2022', 'Simulado']);
    expect(chart.series?.length).toBe(6);
    const names = chart.series?.map((entry) => entry.name);
    expect(names).toContain('Quantidade simulada');
    expect(names).toContain('ITCD simulado');
    const sim = chart.series?.find((entry) => entry.name === 'ITCD simulado');
    expect(sim?.values).toEqual([null, null, 120]);
    expect(chart.series?.[0].values).toEqual([100, 200, null]);
  });

  it('ignores an empty scenario in the chart', () => {
    const rows = publicByYear(items, [2021], 'Vendas', 'SP');
    const chart = simulatorChart(rows, [], 'SP', { quantity: null, value: null });
    expect(chart.categories).toEqual(['2021']);
  });
});
