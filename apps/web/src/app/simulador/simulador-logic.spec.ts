import { SpedSerieItem } from '../sped-operacoes/sped-logic';
import {
  GOODS_TYPES,
  ICMS_RATE_BY_UF,
  RateVersion,
  TAXES,
  fallbackVersions,
  resolveRate,
} from './simulador-aliquotas';
import {
  HYPOTHESIS_LABEL,
  allowedParam,
  hypothesisChart,
  publicByYear,
  referenceYear,
  sanitize,
  scenarioComparison,
  simulatorChart,
  taxAmount,
  rateLabel,
  taxByYear,
} from './simulador-logic';
import { HEX_LAYOUT } from '../atlas/hex-layout';

const items: SpedSerieItem[] = [
  { ano: 2021, uf: 'SP', operacao: 'Vendas', quantidade: 100, valorEstimado: '1000.00' },
  { ano: 2022, uf: 'SP', operacao: 'Vendas', quantidade: 200, valorEstimado: null },
  { ano: 2022, uf: 'SP', operacao: 'Compras', quantidade: 999, valorEstimado: '9999.00' },
  { ano: 2021, uf: 'AC', operacao: 'Vendas', quantidade: 10, valorEstimado: '50.00' },
];

const book = fallbackVersions();

function acre(): RateVersion[] {
  const common = { tax: 'ICMS' as const, uf: 'AC', rateKind: 'MODAL', legalBasis: 'LC/AC 422/2022', officialUrl: null, status: 'VALIDADO' as const, note: null };
  return [
    { ...common, rate: 17, validFrom: null, validTo: '2023-03-31' },
    { ...common, rate: 19, validFrom: '2023-04-01', validTo: null },
  ];
}

describe('simulador aliquotas', () => {
  it('uses the fixed rates from the requirement, all pending legal validation', () => {
    expect(resolveRate(book, 'ITCD', null, 2024).rate).toBe(6);
    expect(resolveRate(book, 'ITBI', 'SP', 2024).rate).toBe(3);
    expect(resolveRate(book, 'ISS', null, 2024).rate).toBe(5);
    expect(resolveRate(book, 'ITCD', null, 2024).status).toBe('PENDENTE');
  });

  it('has an ICMS rate for each of the 27 UFs in the fallback and fails closed for the rest', () => {
    expect(Object.keys(ICMS_RATE_BY_UF).sort()).toEqual(HEX_LAYOUT.map((cell) => cell.uf).sort());
    expect(resolveRate(book, 'ICMS', 'SP', 2024).rate).toBe(18);
    expect(resolveRate(book, 'ICMS', 'MA', 2024).rate).toBe(23);
    expect(resolveRate(book, 'ICMS', 'PI', 2024).rate).toBe(22.5);
    expect(resolveRate(book, 'ICMS', null, 2024).rate).toBeNull();
    expect(resolveRate(book, 'ICMS', 'XX', 2024).rate).toBeNull();
    expect(book.every((version) => version.status === 'PENDENTE' && version.legalBasis === null)).toBeTrue();
  });

  it('uses the Acre rate in force in each year and leaves the year of the change empty', () => {
    const ac = acre();
    expect(resolveRate(ac, 'ICMS', 'AC', 2021)).toEqual(jasmine.objectContaining({ rate: 17, status: 'VALIDADO' }));
    expect(resolveRate(ac, 'ICMS', 'AC', 2022).rate).toBe(17);
    const changed = resolveRate(ac, 'ICMS', 'AC', 2023);
    expect(changed.rate).toBeNull();
    expect(changed.changedWithinYear).toBeTrue();
    expect(resolveRate(ac, 'ICMS', 'AC', 2024).rate).toBe(19);
    expect(resolveRate(ac, 'ICMS', 'AC', 2025).rate).toBe(19);
  });

  it('prefers a validated rate over a pending one and ignores revoked versions', () => {
    const pending = fallbackVersions().filter((version) => version.uf === 'AC');
    const merged = [...pending, ...acre()];
    expect(resolveRate(merged, 'ICMS', 'AC', 2024).status).toBe('VALIDADO');
    expect(resolveRate(merged, 'ICMS', 'AC', 2024).rate).toBe(19);
    const revoked = acre().map((version) => ({ ...version, status: 'REVOGADO' as const }));
    expect(resolveRate(revoked, 'ICMS', 'AC', 2024).rate).toBeNull();
  });

  it('labels the rate with its status', () => {
    expect(rateLabel('ICMS', resolveRate(book, 'ICMS', 'SP', 2024))).toBe('ICMS 18% (pendente)');
    expect(rateLabel('ICMS', resolveRate(acre(), 'ICMS', 'AC', 2024))).toBe('ICMS 19%');
    expect(rateLabel('ICMS', resolveRate(acre(), 'ICMS', 'AC', 2023))).toBe('ICMS (alíquota mudou no ano)');
    expect(rateLabel('ICMS', resolveRate(book, 'ICMS', null, 2024))).toBe('ICMS (sem alíquota)');
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
    expect(taxByYear(rows, 'ITCD', 'SP', book)).toEqual([60, null, null]);
    expect(taxByYear(rows, 'ICMS', null, book)).toEqual([null, null, null]);
  });

  it('compares the scenario with the public year and the tax difference', () => {
    const rows = publicByYear(items, [2021], 'Vendas', 'SP');
    const table = scenarioComparison(referenceYear(rows, 2021), { quantity: 150, value: 2000 }, ['ITCD', 'ICMS'], 'SP', book);
    expect(table.map((row) => row.label)).toEqual(['Quantidade', 'Valor', 'ITCD 6% (pendente)', 'ICMS 18% (pendente)']);
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
    const table = scenarioComparison(referenceYear(rows, 2022), { quantity: 5, value: 100 }, ['ISS'], 'SP', book);
    expect(table[1].publicValue).toBeNull();
    expect(table[1].difference).toBeNull();
    expect(table[1].differencePercent).toBeNull();
    expect(table[2].difference).toBeNull();
    const none = scenarioComparison(null, { quantity: null, value: null }, ['ISS'], null, book);
    expect(none.every((row) => row.simulated === null && row.difference === null)).toBeTrue();
  });

  it('uses the Acre rate of each year in the table and in the scenario', () => {
    const acItems: SpedSerieItem[] = [2022, 2023, 2024].map((ano) => ({
      ano,
      uf: 'AC',
      operacao: 'Vendas',
      quantidade: 10,
      valorEstimado: '1000.00',
    }));
    const rows = publicByYear(acItems, [2022, 2023, 2024], 'Vendas', 'AC');
    expect(taxByYear(rows, 'ICMS', 'AC', acre())).toEqual([170, null, 190]);
    const in2024 = scenarioComparison(referenceYear(rows, 2024), { quantity: 1, value: 2000 }, ['ICMS'], 'AC', acre());
    expect(in2024[2].label).toBe('ICMS 19%');
    expect(in2024[2].simulated).toBe(380);
    const in2023 = scenarioComparison(referenceYear(rows, 2023), { quantity: 1, value: 2000 }, ['ICMS'], 'AC', acre());
    expect(in2023[2].label).toBe('ICMS (alíquota mudou no ano)');
    expect(in2023[2].simulated).toBeNull();
    expect(in2023[2].difference).toBeNull();
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
    const plain = simulatorChart(rows, ['ITCD'], 'SP', null, book);
    expect(plain.categories).toEqual(['2021', '2022']);
    expect(plain.series?.map((entry) => entry.name)).toEqual([
      'Quantidade',
      'Valor',
      'ITCD apurado',
    ]);
    expect(plain.series?.[1].axis).toBe('right');

    const chart = simulatorChart(rows, ['ITCD'], 'SP', { quantity: 150, value: 2000 }, book);
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
    const chart = simulatorChart(rows, [], 'SP', { quantity: null, value: null }, book);
    expect(chart.categories).toEqual(['2021']);
  });
});

describe('hypothesisChart', () => {
  it('has one point per series and no public data', () => {
    const chart = hypothesisChart({ quantity: 150, value: 2000 }, ['ITCD', 'ICMS'], 'SP', book, 2024);
    expect(chart.categories).toEqual([HYPOTHESIS_LABEL]);
    expect(chart.series?.map((entry) => entry.name)).toEqual([
      'Quantidade (hipótese)',
      'Valor (hipótese)',
      'ITCD (hipótese)',
      'ICMS (hipótese)',
    ]);
    expect(chart.series?.map((entry) => entry.values)).toEqual([[150], [2000], [120], [360]]);
  });

  it('keeps an absent input empty and never turns it into zero', () => {
    const chart = hypothesisChart({ quantity: 10, value: null }, ['ITCD'], null, book);
    expect(chart.series?.[1].values).toEqual([null]);
    expect(chart.series?.[2].values).toEqual([null]);
  });
});