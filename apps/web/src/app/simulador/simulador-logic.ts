/**
 * Regras puras do Simulador. Imposto = valor x aliquota. Quantidade e observada, o valor
 * publico vem da planilha (rateio) e o imposto e simulacao aritmetica, nao apuracao fiscal.
 * Nada aqui soma operacoes ou impostos diferentes. Valor ausente nunca vira zero.
 */
import { BiChartInput } from '../shared/bi/bi-chart-options';
import { SpedSerieItem, byYear } from '../sped-operacoes/sped-logic';
import { TaxId, rateFor } from './simulador-aliquotas';

export const SIMULATED_LABEL = 'Simulado';

export interface PublicYear {
  year: number;
  quantity: number | null;
  value: number | null;
}

/** Imposto em reais, arredondado ao centavo. Sem valor ou sem aliquota o resultado e nulo. */
export function taxAmount(value: number | null, rate: number | null): number | null {
  if (value === null || rate === null || !Number.isFinite(value) || !Number.isFinite(rate)) {
    return null;
  }
  return Math.round(value * rate) / 100;
}

/** Quantidade e valor publicos por ano para uma UF (ou Brasil) e uma unica operacao. */
export function publicByYear(
  items: SpedSerieItem[],
  years: number[],
  operation: string,
  uf: string | null,
): PublicYear[] {
  const quantity = byYear(items, years, operation, 'quantidade', uf);
  const value = byYear(items, years, operation, 'valor', uf);
  return years.map((year, index) => ({ year, quantity: quantity[index], value: value[index] }));
}

/** Imposto apurado por ano para cada imposto escolhido. */
export function taxByYear(rows: PublicYear[], tax: TaxId, uf: string | null): (number | null)[] {
  const rate = rateFor(tax, uf);
  return rows.map((row) => taxAmount(row.value, rate));
}

export interface ScenarioInput {
  quantity: number | null;
  value: number | null;
}

/** Entrada valida: numero finito e nao negativo. Qualquer outra coisa e tratada como ausente. */
export function sanitize(raw: number | null | undefined): number | null {
  return typeof raw === 'number' && Number.isFinite(raw) && raw >= 0 ? raw : null;
}

export interface Comparison {
  label: string;
  unit: 'COUNT' | 'BRL';
  publicValue: number | null;
  simulated: number | null;
  difference: number | null;
  differencePercent: number | null;
}

export function compare(
  label: string,
  unit: 'COUNT' | 'BRL',
  publicValue: number | null,
  simulated: number | null,
): Comparison {
  const difference = publicValue === null || simulated === null ? null : simulated - publicValue;
  const percent =
    difference === null || publicValue === null || publicValue === 0 ? null : (difference / publicValue) * 100;
  return { label, unit, publicValue, simulated, difference, differencePercent: percent };
}

/** Quadro da Parte B: quantidade, valor e um imposto por linha, publico x simulado. */
export function scenarioComparison(
  reference: PublicYear | null,
  scenario: ScenarioInput,
  taxes: TaxId[],
  uf: string | null,
): Comparison[] {
  const rows: Comparison[] = [
    compare('Quantidade', 'COUNT', reference?.quantity ?? null, scenario.quantity),
    compare('Valor', 'BRL', reference?.value ?? null, scenario.value),
  ];
  for (const tax of taxes) {
    const rate = rateFor(tax, uf);
    rows.push(
      compare(
        `${tax}${rate === null ? ' (sem alíquota)' : ' ' + rate.toLocaleString('pt-BR') + '%'}`,
        'BRL',
        taxAmount(reference?.value ?? null, rate),
        taxAmount(scenario.value, rate),
      ),
    );
  }
  return rows;
}

function simulatedOnly(length: number, last: number | null): (number | null)[] {
  return Array.from({ length }, (_, index) => (index === length - 1 ? last : null));
}

/**
 * Grafico com todos os dados publicos por ano e, quando ha cenario, uma categoria "Simulado"
 * com pontos proprios. Quantidade no eixo esquerdo; valor e impostos (R$) no eixo direito.
 */
export function simulatorChart(
  rows: PublicYear[],
  taxes: TaxId[],
  uf: string | null,
  scenario: ScenarioInput | null,
): BiChartInput {
  const years = rows.map((row) => String(row.year));
  const withScenario = scenario !== null && (scenario.quantity !== null || scenario.value !== null);
  const categories = withScenario ? [...years, SIMULATED_LABEL] : years;
  const pad = (values: (number | null)[]): (number | null)[] => (withScenario ? [...values, null] : values);
  const series: BiChartInput['series'] = [
    { name: 'Quantidade', values: pad(rows.map((row) => row.quantity)), unit: 'COUNT' },
    { name: 'Valor', values: pad(rows.map((row) => row.value)), axis: 'right', unit: 'BRL' },
  ];
  for (const tax of taxes) {
    series.push({
      name: `${tax} apurado`,
      values: pad(taxByYear(rows, tax, uf)),
      axis: 'right',
      unit: 'BRL',
    });
  }
  if (withScenario && scenario) {
    const size = categories.length;
    series.push({
      name: 'Quantidade simulada',
      values: simulatedOnly(size, scenario.quantity),
      unit: 'COUNT',
      dashed: true,
      colorLike: 'Quantidade',
    });
    series.push({
      name: 'Valor simulado',
      values: simulatedOnly(size, scenario.value),
      axis: 'right',
      unit: 'BRL',
      dashed: true,
      colorLike: 'Valor',
    });
    for (const tax of taxes) {
      series.push({
        name: `${tax} simulado`,
        values: simulatedOnly(size, taxAmount(scenario.value, rateFor(tax, uf))),
        axis: 'right',
        unit: 'BRL',
        dashed: true,
        colorLike: `${tax} apurado`,
      });
    }
  }
  return { kind: 'line', unit: 'COUNT', categories, series };
}

/** Valor vindo da URL so vale se estiver na lista conhecida. Qualquer outro cai no padrao. */
export function allowedParam(raw: string | null | undefined, allowed: readonly string[], fallback: string): string {
  return raw && allowed.includes(raw) ? raw : fallback;
}

/** Linha de referencia da Parte B para o ano escolhido. */
export function referenceYear(rows: PublicYear[], year: number | null): PublicYear | null {
  if (rows.length === 0) {
    return null;
  }
  return rows.find((row) => row.year === year) ?? rows[rows.length - 1];
}