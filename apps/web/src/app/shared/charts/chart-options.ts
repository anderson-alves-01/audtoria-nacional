import { EChartsOption } from 'echarts';
import {
  compactPublishedValue,
  formatPublishedValue,
  humanizeUnit,
} from '../presentation/official-labels';
import { ChartTheme, readChartTheme } from './chart-theme';

export interface ChartPoint {
  x: string;
  y: number;
}

export function buildChartOptions(input: {
  chartType: 'line' | 'bar';
  seriesName: string;
  points: ChartPoint[];
  unit: string;
  theme?: ChartTheme;
}): EChartsOption {
  const theme = input.theme ?? readChartTheme();
  const line = input.chartType === 'line';
  const values = input.points.map((point) => point.y);
  return {
    color: [theme.accent],
    textStyle: { fontFamily: theme.fontUi, color: theme.text2 },
    animationDuration: 300,
    tooltip: {
      trigger: 'axis',
      backgroundColor: theme.surface,
      borderColor: theme.line,
      textStyle: { color: theme.text },
      axisPointer: { type: 'line', lineStyle: { color: theme.muted, type: 'dashed' } },
      formatter: (params: unknown) => formatChartTooltip(params, input.unit),
    },
    legend: {
      show: true,
      top: 0,
      left: 'center',
      icon: 'roundRect',
      itemWidth: 18,
      itemHeight: 4,
      textStyle: { color: theme.text2 },
    },
    grid: { left: 72, right: 24, top: line ? 72 : 36, bottom: 36 },
    xAxis: {
      type: 'category',
      data: input.points.map((point) => point.x),
      boundaryGap: !line,
      axisLine: { lineStyle: { color: theme.line } },
      axisTick: { show: false },
      axisLabel: { color: theme.text2, rotate: input.points.length > 8 ? 35 : 0 },
    },
    yAxis: {
      type: 'value',
      scale: line,
      axisLabel: {
        color: theme.muted,
        fontFamily: theme.fontNum,
        formatter: (value: number) => compactPublishedValue(value, input.unit),
      },
      splitLine: { lineStyle: { color: theme.line, type: 'dashed' } },
    },
    series: [
      {
        name: input.seriesName,
        type: line ? 'line' : 'bar',
        data: values,
        smooth: 0.35,
        symbol: 'circle',
        symbolSize: line ? 8 : 0,
        lineStyle: { width: 3, color: theme.accent },
        itemStyle: { color: theme.accent, borderRadius: line ? 0 : [4, 4, 0, 0] },
        areaStyle: line ? { color: theme.accentSoft } : undefined,
        emphasis: { focus: 'series' },
        barMaxWidth: 36,
        label: {
          show: line,
          position: 'top',
          distance: 8,
          color: theme.accent,
          fontFamily: theme.fontNum,
          fontWeight: 600,
          backgroundColor: theme.surface,
          borderColor: theme.line,
          borderWidth: 1,
          borderRadius: 6,
          padding: [3, 6],
          formatter: (params: { value?: unknown }) => {
            const raw = Array.isArray(params.value) ? params.value[1] : params.value;
            return compactPublishedValue(Number(raw), input.unit);
          },
        },
      },
    ],
  };
}

function formatChartTooltip(params: unknown, unit: string): string {
  const row = Array.isArray(params) ? params[0] : params;
  const item = (row || {}) as { name?: string; value?: unknown; seriesName?: string };
  const raw = Array.isArray(item.value) ? item.value[1] : item.value;
  const amount = formatPublishedValue(Number(raw), unit);
  const unitLabel =
    unit && !['BRL', 'COUNT', 'UNIT', 'MIXED'].includes(unit) ? ` ${humanizeUnit(unit)}` : '';
  return `${item.name || ''}<br/>${item.seriesName || 'Série'}: ${amount}${unitLabel}`;
}
