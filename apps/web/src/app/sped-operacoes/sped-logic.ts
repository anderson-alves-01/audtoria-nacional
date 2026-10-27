/**
 * Regras puras do painel SPED por UF. Quantidade é observada. O valor em R$ é rateio estimado.
 * Nada aqui soma operações diferentes e valor ausente nunca vira zero.
 */
import { HEX_LAYOUT, HexCell } from '../atlas/hex-layout';
import { BiChartInput, toIndexValues } from '../shared/bi/bi-chart-options';

export interface SpedSerieItem {
  ano: number;
  uf: string;
  operacao: string;
  quantidade: number;
  valorEstimado: string | null;
}

export interface SpedCfopItem extends SpedSerieItem {
  cfop: string;
}

export interface SpedRun {
  runId: string;
  checksum: string;
  layoutVersion: string;
  competence: string;
  loadedAt: string;
  receivedCount: number;
}

export interface SpedView<T> {
  sourceId: string;
  valueKind: string;
  banner: string;
  formula: string;
  homologated: boolean;
  published: boolean;
  createsTaxCredit: boolean;
  level: string;
  page: number;
  pageSize: number;
  total: number;
  years: number[];
  operations: string[];
  ufs: string[];
  run: SpedRun | null;
  items: T[];
}

export type Measure = 'quantidade' | 'valor';

export interface SpedFilter {
  ano: string | null;
  uf: string | null;
  operacao: string | null;
}

export const DEFAULT_OPERATION = 'Vendas';
export const EMPTY = '—';

export function money(raw: string | null | undefined): number | null {
  if (raw === null || raw === undefined || raw === '') {
    return null;
  }
  const value = Number(raw);
  return Number.isFinite(value) ? value : null;
}

export function formatMeasure(value: number | null, measure: Measure): string {
  if (value === null) {
    return EMPTY;
  }
  return measure === 'valor'
    ? value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
    : value.toLocaleString('pt-BR');
}

export function measureOf(item: SpedSerieItem, measure: Measure): number | null {
  return measure === 'quantidade' ? item.quantidade : money(item.valorEstimado);
}

/** Soma só valores existentes. Sem nenhum valor o resultado é nulo, nunca zero. */
export function sumKnown(values: (number | null)[]): number | null {
  let seen = false;
  let sum = 0;
  for (const value of values) {
    if (value !== null) {
      sum += value;
      seen = true;
    }
  }
  return seen ? sum : null;
}

export function pick(items: SpedSerieItem[], filter: Partial<SpedFilter>): SpedSerieItem[] {
  return items.filter(
    (item) =>
      (!filter.ano || String(item.ano) === filter.ano) &&
      (!filter.uf || item.uf === filter.uf) &&
      (!filter.operacao || item.operacao === filter.operacao),
  );
}

/** Valor por UF de uma única operação, somando os anos escolhidos. Nunca mistura operações. */
export function byUf(
  items: SpedSerieItem[],
  operation: string,
  measure: Measure,
  ano: string | null,
): Map<string, number | null> {
  const out = new Map<string, number | null>();
  for (const cell of HEX_LAYOUT) {
    const rows = pick(items, { ano, uf: cell.uf, operacao: operation });
    out.set(cell.uf, rows.length === 0 ? null : sumKnown(rows.map((row) => measureOf(row, measure))));
  }
  return out;
}

/** Um valor por operação, cada um separado. Não existe total entre operações. */
export function byOperation(
  items: SpedSerieItem[],
  operations: string[],
  measure: Measure,
  filter: Pick<SpedFilter, 'ano' | 'uf'>,
): Map<string, number | null> {
  const out = new Map<string, number | null>();
  for (const operation of operations) {
    const rows = pick(items, { ...filter, operacao: operation });
    out.set(operation, rows.length === 0 ? null : sumKnown(rows.map((row) => measureOf(row, measure))));
  }
  return out;
}

export function byYear(
  items: SpedSerieItem[],
  years: number[],
  operation: string,
  measure: Measure,
  uf: string | null,
): (number | null)[] {
  return years.map((year) => {
    const rows = pick(items, { ano: String(year), uf, operacao: operation });
    return rows.length === 0 ? null : sumKnown(rows.map((row) => measureOf(row, measure)));
  });
}

export type CompareMode = 'eixos' | 'indice';

export const QUANTITY_UNIT = 'COUNT';
export const VALUE_UNIT = 'BRL';
export const INDEX_UNIT = 'INDEX';

/**
 * Grafico unico com duas linhas: quantidade observada e valor estimado. Em "eixos" cada linha
 * usa seu proprio eixo (esquerdo e direito). Em "indice" as duas partem de 100 no primeiro
 * valor existente e dividem o mesmo eixo. Valor ausente continua lacuna.
 */
export function comparisonChart(
  categories: string[],
  quantity: (number | null)[],
  value: (number | null)[],
  mode: CompareMode,
  names: { quantity: string; value: string },
  extra: Partial<Pick<BiChartInput, 'selected'>> = {},
): BiChartInput {
  if (mode === 'indice') {
    return {
      kind: 'line',
      unit: INDEX_UNIT,
      categories,
      series: [
        { name: `${names.quantity} (índice)`, values: toIndexValues(quantity) },
        { name: `${names.value} (índice)`, values: toIndexValues(value) },
      ],
      ...extra,
    };
  }
  return {
    kind: 'line',
    unit: QUANTITY_UNIT,
    categories,
    series: [
      { name: names.quantity, values: quantity, unit: QUANTITY_UNIT },
      { name: names.value, values: value, axis: 'right', unit: VALUE_UNIT },
    ],
    ...extra,
  };
}

export interface HexShape {
  cell: HexCell;
  cx: number;
  cy: number;
  path: string;
}

export const HEX_RADIUS = 34;

export function hexShapes(): HexShape[] {
  const sx = Math.sqrt(3) * HEX_RADIUS;
  const sy = 1.5 * HEX_RADIUS;
  return HEX_LAYOUT.map((cell) => {
    const cx = (cell.col + (cell.row % 2 ? 0.5 : 0)) * sx;
    const cy = cell.row * sy;
    const points: string[] = [];
    for (let step = 0; step < 6; step += 1) {
      const angle = ((-90 + 60 * step) * Math.PI) / 180;
      points.push(`${(cx + HEX_RADIUS * Math.cos(angle)).toFixed(1)},${(cy + HEX_RADIUS * Math.sin(angle)).toFixed(1)}`);
    }
    return { cell, cx, cy, path: `M${points.join('L')}Z` };
  });
}

/**
 * Com uma UF escolhida so o hexagono dela fica visivel. Sem escolha, ou com UF desconhecida,
 * aparecem as 27. Falha aberta so na exibicao: o filtro dos dados nao muda.
 */
export function visibleShapes(shapes: HexShape[], selected: string | null): HexShape[] {
  if (!selected) {
    return shapes;
  }
  const only = shapes.filter((shape) => shape.cell.uf === selected);
  return only.length > 0 ? only : shapes;
}

/** Caixa de visualizacao SVG que envolve os hexagonos exibidos. */
export function viewBoxFor(shapes: HexShape[]): string {
  if (shapes.length === 0) {
    return '-40 -48 545 420';
  }
  if (shapes.length === HEX_LAYOUT.length) {
    return '-40 -48 545 420';
  }
  const pad = 14;
  const xs = shapes.map((shape) => shape.cx);
  const ys = shapes.map((shape) => shape.cy);
  const minX = Math.min(...xs) - HEX_RADIUS - pad;
  const minY = Math.min(...ys) - HEX_RADIUS - pad;
  const width = Math.max(...xs) - Math.min(...xs) + 2 * (HEX_RADIUS + pad);
  const height = Math.max(...ys) - Math.min(...ys) + 2 * (HEX_RADIUS + pad);
  return `${minX.toFixed(1)} ${minY.toFixed(1)} ${width.toFixed(1)} ${height.toFixed(1)}`;
}

/** Faixa de 0 a 1 entre o menor e o maior valor existente. Valor ausente devolve nulo. */
export function intensity(value: number | null, min: number, max: number): number | null {
  if (value === null) {
    return null;
  }
  if (max <= min) {
    return 1;
  }
  return (value - min) / (max - min);
}

export function bounds(values: Iterable<number | null>): { min: number; max: number } | null {
  let min = Infinity;
  let max = -Infinity;
  for (const value of values) {
    if (value !== null) {
      min = Math.min(min, value);
      max = Math.max(max, value);
    }
  }
  return min === Infinity ? null : { min, max };
}
