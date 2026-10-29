/**
 * Regras puras do Simulador. Imposto = valor x aliquota. Quantidade e valor publicos da CGU
 * NF-e (itens e valor dos itens, exceto canceladas, UF do emitente). O imposto e simulacao
 * aritmetica, nao apuracao fiscal. Valor ausente nunca vira zero.
 */
import { BiChartInput } from '../shared/bi/bi-chart-options';
import { ReliabilityBlock } from '../shared/reliability/indicator-reliability';
import { SpedSerieItem, byYear, money } from '../sped-operacoes/sped-logic';
import { RateVersion, ResolvedRate, TaxId, resolveRate } from './simulador-aliquotas';

export const SIMULATED_LABEL = 'Simulado';

/** Ano usado para a aliquota quando nao ha ano publico de referencia (sem carga). */
export const referenceFallbackYear = 2025;

export interface PublicYear {
  year: number;
  quantity: number | null;
  value: number | null;
}

/**
 * Imposto em reais, arredondado ao centavo (meio para cima). Sem valor ou sem aliquota o resultado e
 * nulo. O produto binario carrega ruido (4,06 x 25 da 101,49999999999999), entao ele e limpo a 15
 * digitos significativos antes de arredondar. Se o resultado nao couber em centavos inteiros num
 * numero de ponto flutuante, fica nulo: nunca um valor aproximado nem infinito.
 */
export function taxAmount(value: number | null, rate: number | null): number | null {
  if (value === null || rate === null || !Number.isFinite(value) || !Number.isFinite(rate)) {
    return null;
  }
  const product = value * rate;
  if (!Number.isFinite(product) || Math.abs(product) > MAX_EXACT_CENTS) {
    return null;
  }
  const cents = Math.round(Number(product.toPrecision(15)));
  return (cents === 0 ? 0 : cents) / 100;
}

/** Maior produto valor x aliquota (em centavos) que ainda e um inteiro exato: 2^53 - 1. */
const MAX_EXACT_CENTS = Number.MAX_SAFE_INTEGER;

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

export interface CguNfeItem {
  ano: number;
  uf: string;
  itens: number;
  valorItens: string | null;
}

export interface CguNfeRun {
  runId: string;
  layoutVersion: string;
  competence: string;
  monthsProcessed: number;
  loadedAt?: string | null;
}

export interface CguNfeView {
  sourceId: string;
  valueKind: string;
  banner: string;
  formula: string;
  homologated: boolean;
  published: boolean;
  createsTaxCredit: boolean;
  reliability?: ReliabilityBlock;
  coverage: string;
  monthsProcessed: number;
  monthsMissing: string[];
  page: number;
  pageSize: number;
  total: number;
  years: number[];
  ufs: string[];
  run: CguNfeRun | null;
  items: CguNfeItem[];
}

/**
 * Serie publica da CGU: itens e valor dos itens (exceto canceladas) por ano.
 * Sem operacao. UF vazia soma as UFs presentes. Ano sem linha fica nulo, nunca zero.
 */
export function publicByYearFromCgu(items: CguNfeItem[], years: number[], uf: string | null): PublicYear[] {
  return years.map((year) => {
    const rows = items.filter((item) => item.ano === year && (uf === null || item.uf === uf));
    if (rows.length === 0) {
      return { year, quantity: null, value: null };
    }
    const quantity = rows.reduce((sum, item) => sum + item.itens, 0);
    const values = rows.map((item) => money(item.valorItens)).filter((value): value is number => value !== null);
    return { year, quantity, value: values.length === 0 ? null : values.reduce((sum, value) => sum + value, 0) };
  });
}

/** Imposto estimado por ano (simulacao) para cada imposto escolhido, com a aliquota vigente em cada ano. */
export function taxByYear(
  rows: PublicYear[],
  tax: TaxId,
  uf: string | null,
  book: RateVersion[],
  municipality: string | null = null,
): (number | null)[] {
  return rows.map((row) => taxAmount(row.value, resolveRate(book, tax, uf, row.year, municipality).rate));
}

/** Rotulo curto da aliquota no quadro: percentual e situacao (pendente, mudou no ano, ausente). */
export function rateLabel(tax: TaxId, resolved: ResolvedRate): string {
  if (resolved.changedWithinYear) {
    return `${tax} (alíquota mudou no ano)`;
  }
  if (resolved.rate === null) {
    return `${tax} (sem alíquota)`;
  }
  const percent = `${tax} ${resolved.rate.toLocaleString('pt-BR')}%`;
  if (resolved.isSimulation) {
    return `${percent} (parâmetro de simulação)`;
  }
  return resolved.status === 'PENDENTE' ? `${percent} (pendente)` : percent;
}

export const TRANSFER_OPERATION = 'Transferências';
export type TransferDirection = '' | 'RECEBIDA' | 'REMETIDA';
export const TRANSFER_DIRECTION_LABEL: Record<'RECEBIDA' | 'REMETIDA', string> = {
  RECEBIDA: 'Transferências recebidas',
  REMETIDA: 'Transferências remetidas',
};
export const TRANSFER_DIRECTION_NOTE =
  'Transferências recebidas e remetidas nunca são somadas: o mesmo movimento pode aparecer nas duas direções e a soma duplicaria a contagem. Uma contagem distinta exige identificar os documentos ou uma regra de deduplicação comprovada.';
export const TRANSFER_ICMS_NOTE =
  'ICMS não calculado: a transferência entre estabelecimentos do mesmo titular, em regra, não é fato gerador (LC 204/2023, informada pelo responsável, a conferir na fonte), com regras próprias de crédito e uma opção legal de equiparação.';

/** ICMS fica em branco numa transferencia, a menos que a pessoa opte, como hipotese, por calcula-lo. */
export function icmsBlockedForTransfer(operation: string, optIn: boolean): boolean {
  return operation === TRANSFER_OPERATION && !optIn;
}

/** Impostos que entram nos calculos: remove o ICMS de uma transferencia sem opt-in. */
export function effectiveTaxes(taxes: TaxId[], operation: string, optIn: boolean): TaxId[] {
  return icmsBlockedForTransfer(operation, optIn) ? taxes.filter((tax) => tax !== 'ICMS') : taxes;
}

/**
 * Dado publico de transferencia so vale para UMA direcao. Sem direcao escolhida, ou sem o campo
 * `direcao` no item, nada entra (falha fechada): somar as duas direcoes duplicaria a contagem.
 */
export function filterByDirection(
  items: SpedSerieItem[],
  operation: string,
  direction: TransferDirection,
): SpedSerieItem[] {
  if (operation !== TRANSFER_OPERATION) {
    return items;
  }
  if (direction === '') {
    return [];
  }
  return items.filter((item) => item.operacao === TRANSFER_OPERATION && item.direcao === direction);
}

export interface ScenarioInput {
  quantity: number | null;
  value: number | null;
}

/** Entrada valida: numero finito e nao negativo. Qualquer outra coisa e tratada como ausente. */
export function sanitize(raw: number | null | undefined): number | null {
  // Somar 0 troca -0 por 0: o Intl mostraria "-R$ 0,00".
  return typeof raw === 'number' && Number.isFinite(raw) && raw >= 0 ? raw + 0 : null;
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
  book: RateVersion[],
  municipality: string | null = null,
): Comparison[] {
  const rows: Comparison[] = [
    compare('Quantidade', 'COUNT', reference?.quantity ?? null, scenario.quantity),
    compare('Valor', 'BRL', reference?.value ?? null, scenario.value),
  ];
  for (const tax of taxes) {
    // A aliquota e a vigente no ano de comparacao, para o publico e para o cenario.
    const resolved = resolveRate(book, tax, uf, reference?.year ?? referenceFallbackYear, municipality);
    rows.push(
      compare(
        rateLabel(tax, resolved),
        'BRL',
        taxAmount(reference?.value ?? null, resolved.rate),
        taxAmount(scenario.value, resolved.rate),
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
  book: RateVersion[],
  scenarioYear: number = referenceFallbackYear,
  municipality: string | null = null,
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
      name: `${tax} estimado`,
      values: pad(taxByYear(rows, tax, uf, book, municipality)),
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
        values: simulatedOnly(size, taxAmount(scenario.value, resolveRate(book, tax, uf, scenarioYear, municipality).rate)),
        axis: 'right',
        unit: 'BRL',
        dashed: true,
        colorLike: `${tax} estimado`,
      });
    }
  }
  return { kind: 'line', unit: 'COUNT', categories, series };
}

/** Rotulo de tudo que o Simulador calcula a partir do que a pessoa digitou. */
export const HYPOTHESIS_LABEL = 'Hipótese informada manualmente';

/**
 * Grafico da hipotese informada: um unico ponto por serie, sem nenhum dado publico. Usado enquanto
 * o dado publico estiver bloqueado. Quantidade a esquerda; valor e impostos (R$) a direita.
 */
export function hypothesisChart(
  scenario: ScenarioInput,
  taxes: TaxId[],
  uf: string | null,
  book: RateVersion[],
  year: number = referenceFallbackYear,
  municipality: string | null = null,
): BiChartInput {
  const series: BiChartInput['series'] = [
    { name: 'Quantidade (hipótese)', values: [scenario.quantity], unit: 'COUNT', dashed: true },
    { name: 'Valor (hipótese)', values: [scenario.value], axis: 'right', unit: 'BRL', dashed: true },
  ];
  for (const tax of taxes) {
    series.push({
      name: `${tax} (hipótese)`,
      values: [taxAmount(scenario.value, resolveRate(book, tax, uf, year, municipality).rate)],
      axis: 'right',
      unit: 'BRL',
      dashed: true,
    });
  }
  return { kind: 'line', unit: 'COUNT', categories: [HYPOTHESIS_LABEL], series };
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