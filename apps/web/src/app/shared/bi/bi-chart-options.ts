import { EChartsOption } from 'echarts';
import { ChartTheme, readChartTheme } from '../charts/chart-theme';
import { compactPublishedValue, formatPublishedValue } from '../presentation/official-labels';

export type BiChartKind = 'bar' | 'barH' | 'line' | 'area' | 'scatter' | 'treemap' | 'funnel' | 'heatmap';

export interface BiSeries {
  name: string;
  values: (number | null)[];
  /** Eixo vertical da serie. Padrao: esquerdo. O direito aceita outra unidade. */
  axis?: 'left' | 'right';
  /** Unidade propria da serie (tooltip, tabela e eixo direito). Padrao: a do grafico. */
  unit?: string;
  /** Linha tracejada com ponto maior: usada para cenario simulado. */
  dashed?: boolean;
  /** Reaproveita a cor de outra serie (pelo nome), para parear publico e simulado. */
  colorLike?: string;
}

/**
 * Reescala uma serie para base 100 no primeiro valor existente. Vazio continua vazio e
 * base nula ou zero nao permite indice (tudo fica vazio, nunca inventado).
 */
export function toIndexValues(values: (number | null)[]): (number | null)[] {
  const base = values.find((value): value is number => value !== null);
  if (base === undefined || base === 0) {
    return values.map(() => null);
  }
  return values.map((value) => (value === null ? null : (value / base) * 100));
}

export interface BiChartInput {
  kind: BiChartKind;
  unit: string;
  /** Categorias do eixo (barras, linhas) ou colunas do mapa de calor. */
  categories?: string[];
  series?: BiSeries[];
  /** Linhas do mapa de calor. */
  rowLabels?: string[];
  /** Mapa de calor: [indice da coluna, indice da linha, valor]. Valor nulo fica vazio. */
  cells?: [number, number, number | null][];
  points?: { name: string; x: number; y: number }[];
  items?: { name: string; value: number | null }[];
  /** Categorias em destaque (selecao cruzada). As demais ficam esmaecidas. */
  selected?: string[];
  stacked?: boolean;
  theme?: ChartTheme;
}

const DIM = 0.3;

export function buildBiOptions(input: BiChartInput): EChartsOption {
  const theme = input.theme ?? readChartTheme();
  const base: EChartsOption = {
    color: theme.categorical,
    textStyle: { fontFamily: theme.fontUi, color: theme.text2 },
    animationDuration: 280,
    tooltip: {
      backgroundColor: theme.surface,
      borderColor: theme.line,
      textStyle: { color: theme.text },
    },
  };
  switch (input.kind) {
    case 'scatter':
      return { ...base, ...scatter(input, theme) };
    case 'treemap':
      return { ...base, ...treemap(input, theme) };
    case 'funnel':
      return { ...base, ...funnel(input, theme) };
    case 'heatmap':
      return { ...base, ...heatmap(input, theme) };
    default:
      return { ...base, ...cartesian(input, theme) };
  }
}

function cartesian(input: BiChartInput, theme: ChartTheme): EChartsOption {
  const horizontal = input.kind === 'barH';
  const line = input.kind === 'line' || input.kind === 'area';
  const categories = input.categories ?? [];
  const selected = input.selected ?? [];
  const many = (input.series ?? []).length > 1;
  const seriesList = input.series ?? [];
  const rightSeries = seriesList.find((entry) => entry.axis === 'right');
  const dual = !horizontal && rightSeries !== undefined;
  const valueAxis = {
    type: 'value' as const,
    axisLabel: {
      color: theme.muted,
      fontFamily: theme.fontNum,
      formatter: (value: number) => compactPublishedValue(value, input.unit),
    },
    splitLine: { lineStyle: { color: theme.line, type: 'dashed' as const } },
  };
  const rightAxis = {
    type: 'value' as const,
    position: 'right' as const,
    axisLabel: {
      color: theme.muted,
      fontFamily: theme.fontNum,
      formatter: (value: number) => compactPublishedValue(value, rightSeries?.unit ?? input.unit),
    },
    splitLine: { show: false },
  };
  const categoryAxis = {
    type: 'category' as const,
    data: categories,
    axisLine: { lineStyle: { color: theme.line } },
    axisTick: { show: false },
    axisLabel: { color: theme.text2, rotate: !horizontal && categories.length > 8 ? 35 : 0 },
    inverse: horizontal,
  };
  return {
    legend: many
      ? { show: true, top: 28, icon: 'roundRect', itemWidth: 14, itemHeight: 4, textStyle: { color: theme.text2 } }
      : { show: false },
    grid: {
      left: horizontal ? 120 : 64,
      right: dual ? 84 : 24,
      // A legenda fica abaixo da barra de ferramentas e ganha uma linha a cada 3 series.
      top: many ? 64 + Math.floor((seriesList.length - 1) / 3) * 22 : 28,
      bottom: 56,
    },
    toolbox: {
      right: 8,
      top: 0,
      iconStyle: { borderColor: theme.muted },
      feature: {
        saveAsImage: { title: 'Salvar imagem', name: 'grafico' },
        dataZoom: { title: { zoom: 'Ampliar', back: 'Desfazer' }, yAxisIndex: 'none' },
        restore: { title: 'Restaurar' },
      },
    },
    brush: line || horizontal ? undefined : { toolbox: ['lineX', 'clear'], xAxisIndex: 0, brushStyle: { borderColor: theme.accent, color: theme.accentSoft } },
    dataZoom: categories.length > 18 ? [{ type: 'inside' }, { type: 'slider', height: 14, bottom: 8 }] : [{ type: 'inside' }],
    tooltip: {
      trigger: 'axis',
      backgroundColor: theme.surface,
      borderColor: theme.line,
      textStyle: { color: theme.text },
      axisPointer: { type: 'shadow' },
      formatter: (params: unknown) => axisTooltip(params, input),
    },
    xAxis: horizontal ? valueAxis : categoryAxis,
    yAxis: horizontal ? categoryAxis : dual ? [valueAxis, rightAxis] : valueAxis,
    series: seriesList.map((entry, index) => ({
      name: entry.name,
      yAxisIndex: dual && entry.axis === 'right' ? 1 : 0,
      type: line ? ('line' as const) : ('bar' as const),
      stack: input.stacked ? 'total' : undefined,
      smooth: line ? 0.25 : undefined,
      showSymbol: line,
      symbolSize: entry.dashed ? 11 : 6,
      symbol: entry.dashed ? ('diamond' as const) : undefined,
      areaStyle: input.kind === 'area' ? { opacity: 0.16 } : undefined,
      barMaxWidth: 40,
      emphasis: { focus: 'series' as const },
      lineStyle: { width: 2.5, type: entry.dashed ? ('dashed' as const) : ('solid' as const) },
      connectNulls: false,
      color: theme.categorical[colorIndex(seriesList, entry, index) % theme.categorical.length],
      data: entry.values.map((value, i) => ({
        value,
        itemStyle:
          selected.length > 0 && !selected.includes(categories[i])
            ? { opacity: DIM, borderRadius: horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0] }
            : { borderRadius: horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0] },
      })),
    })),
  };
}

/** Indice de cor da serie: o da serie pareada (colorLike) ou o proprio. */
function colorIndex(all: BiSeries[], entry: BiSeries, own: number): number {
  if (!entry.colorLike) {
    return own;
  }
  const paired = all.findIndex((candidate) => candidate.name === entry.colorLike);
  return paired >= 0 ? paired : own;
}

function scatter(input: BiChartInput, theme: ChartTheme): EChartsOption {
  const points = input.points ?? [];
  return {
    grid: { left: 64, right: 24, top: 28, bottom: 48 },
    tooltip: {
      trigger: 'item',
      backgroundColor: theme.surface,
      borderColor: theme.line,
      textStyle: { color: theme.text },
      formatter: (params: unknown) => {
        const item = params as { data?: { name: string; value: [number, number] } };
        const data = item.data;
        if (!data) {
          return '';
        }
        return `${data.name}<br/>${formatPublishedValue(data.value[0], input.unit)} · ${formatPublishedValue(data.value[1], input.unit)}`;
      },
    },
    xAxis: { type: 'value', axisLabel: { color: theme.muted }, splitLine: { lineStyle: { color: theme.line, type: 'dashed' } } },
    yAxis: { type: 'value', axisLabel: { color: theme.muted }, splitLine: { lineStyle: { color: theme.line, type: 'dashed' } } },
    series: [
      {
        type: 'scatter',
        symbolSize: 11,
        itemStyle: { color: theme.accent, opacity: 0.85 },
        data: points.map((point) => ({ name: point.name, value: [point.x, point.y] })),
      },
    ],
  };
}

function treemap(input: BiChartInput, theme: ChartTheme): EChartsOption {
  const items = (input.items ?? []).filter((item) => typeof item.value === 'number' && (item.value as number) > 0);
  return {
    tooltip: {
      backgroundColor: theme.surface,
      borderColor: theme.line,
      textStyle: { color: theme.text },
      formatter: (params: unknown) => {
        const item = params as { name?: string; value?: number };
        return `${item.name ?? ''}<br/>${formatPublishedValue(Number(item.value), input.unit)}`;
      },
    },
    series: [
      {
        type: 'treemap',
        roam: false,
        nodeClick: false,
        breadcrumb: { show: false },
        label: { color: theme.text, fontFamily: theme.fontUi },
        itemStyle: { borderColor: theme.surface, borderWidth: 2, gapWidth: 2 },
        data: items.map((item, index) => ({
          name: item.name,
          value: item.value as number,
          itemStyle: { color: theme.categorical[index % theme.categorical.length] },
        })),
      },
    ],
  };
}

function funnel(input: BiChartInput, theme: ChartTheme): EChartsOption {
  const items = (input.items ?? []).filter((item) => typeof item.value === 'number');
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: theme.surface,
      borderColor: theme.line,
      textStyle: { color: theme.text },
      formatter: (params: unknown) => {
        const item = params as { name?: string; value?: number };
        return `${item.name ?? ''}<br/>${formatPublishedValue(Number(item.value), input.unit)}`;
      },
    },
    series: [
      {
        type: 'funnel',
        left: '8%',
        width: '84%',
        sort: 'descending',
        gap: 3,
        label: { color: theme.text, fontFamily: theme.fontUi },
        itemStyle: { borderColor: theme.surface, borderWidth: 1 },
        data: items.map((item, index) => ({
          name: item.name,
          value: item.value as number,
          itemStyle: { color: theme.categorical[index % theme.categorical.length] },
        })),
      },
    ],
  };
}

function heatmap(input: BiChartInput, theme: ChartTheme): EChartsOption {
  const cells = (input.cells ?? []).filter((cell) => typeof cell[2] === 'number');
  const values = cells.map((cell) => cell[2] as number);
  return {
    grid: { left: 110, right: 24, top: 16, bottom: 72 },
    tooltip: {
      position: 'top',
      backgroundColor: theme.surface,
      borderColor: theme.line,
      textStyle: { color: theme.text },
      formatter: (params: unknown) => {
        const item = params as { value?: [number, number, number] };
        if (!item.value) {
          return '';
        }
        const column = (input.categories ?? [])[item.value[0]] ?? '';
        const row = (input.rowLabels ?? [])[item.value[1]] ?? '';
        return `${row} · ${column}<br/>${formatPublishedValue(item.value[2], input.unit)}`;
      },
    },
    xAxis: { type: 'category', data: input.categories ?? [], splitArea: { show: false }, axisLabel: { color: theme.text2 } },
    yAxis: { type: 'category', data: input.rowLabels ?? [], axisLabel: { color: theme.text2 } },
    visualMap: {
      min: values.length ? Math.min(...values) : 0,
      max: values.length ? Math.max(...values) : 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 8,
      inRange: { color: theme.sequential },
      textStyle: { color: theme.muted },
    },
    series: [
      {
        type: 'heatmap',
        data: cells,
        itemStyle: { borderColor: theme.surface, borderWidth: 2, borderRadius: 3 },
        emphasis: { itemStyle: { borderColor: theme.text } },
      },
    ],
  };
}

function axisTooltip(params: unknown, input: BiChartInput): string {
  const rows = (Array.isArray(params) ? params : [params]) as {
    axisValueLabel?: string;
    marker?: string;
    seriesName?: string;
    seriesIndex?: number;
    value?: unknown;
  }[];
  const title = rows[0]?.axisValueLabel ?? '';
  const lines = rows.map((row) => {
    const raw = Array.isArray(row.value) ? row.value[1] : row.value;
    const unit = (input.series ?? [])[row.seriesIndex ?? 0]?.unit ?? input.unit;
    const text = typeof raw === 'number' ? formatPublishedValue(raw, unit) : '—';
    return `${row.marker ?? ''} ${row.seriesName ?? ''}: <b>${text}</b>`;
  });
  return [title, ...lines].join('<br/>');
}

/** Linhas da tabela alternativa de um grafico: sempre ha uma leitura sem depender da imagem. */
export function alternativeRows(input: BiChartInput): { label: string; values: (number | null)[] }[] {
  if (input.kind === 'treemap' || input.kind === 'funnel') {
    return (input.items ?? []).map((item) => ({ label: item.name, values: [item.value] }));
  }
  if (input.kind === 'scatter') {
    return (input.points ?? []).map((point) => ({ label: point.name, values: [point.x, point.y] }));
  }
  if (input.kind === 'heatmap') {
    return (input.rowLabels ?? []).map((label, row) => ({
      label,
      values: (input.categories ?? []).map((_, column) => {
        const cell = (input.cells ?? []).find((entry) => entry[0] === column && entry[1] === row);
        return cell ? cell[2] : null;
      }),
    }));
  }
  return (input.categories ?? []).map((label, index) => ({
    label,
    values: (input.series ?? []).map((entry) => entry.values[index] ?? null),
  }));
}

/** Unidade de cada coluna da tabela alternativa (a da serie ou a do grafico). */
export function alternativeUnits(input: BiChartInput): string[] {
  if (input.kind === 'scatter') {
    return [input.unit, input.unit];
  }
  if (input.kind === 'heatmap') {
    return (input.categories ?? []).map(() => input.unit);
  }
  if (input.kind === 'treemap' || input.kind === 'funnel') {
    return [input.unit];
  }
  return (input.series ?? []).map((entry) => entry.unit ?? input.unit);
}

export function alternativeHeaders(input: BiChartInput): string[] {
  if (input.kind === 'treemap' || input.kind === 'funnel') {
    return ['Valor'];
  }
  if (input.kind === 'scatter') {
    return ['Eixo X', 'Eixo Y'];
  }
  if (input.kind === 'heatmap') {
    return input.categories ?? [];
  }
  return (input.series ?? []).map((entry) => entry.name);
}
