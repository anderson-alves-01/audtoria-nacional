import { EChartsOption } from 'echarts';
import {
  compactPublishedValue,
  formatPublishedValue,
  humanizeUnit,
} from '../presentation/official-labels';

export interface ChartPoint {
  x: string;
  y: number;
}

export function buildChartOptions(input: {
  chartType: 'line' | 'bar';
  seriesName: string;
  points: ChartPoint[];
  unit: string;
}): EChartsOption {
  const line = input.chartType === 'line';
  const values = input.points.map((point) => point.y);
  return {
    color: ['#0f766e'],
    tooltip: {
      trigger: 'axis',
      formatter: (params: unknown) => formatChartTooltip(params, input.unit),
    },
    legend: {
      show: true,
      top: 0,
      left: 'center',
      icon: 'roundRect',
      itemWidth: 18,
      itemHeight: 4,
      textStyle: { color: '#172033' },
    },
    grid: { left: 72, right: 24, top: line ? 72 : 36, bottom: 36 },
    xAxis: {
      type: 'category',
      data: input.points.map((point) => point.x),
      boundaryGap: !line,
      axisLine: { lineStyle: { color: '#d5deea' } },
      axisTick: { show: false },
      axisLabel: { color: '#172033', rotate: input.points.length > 8 ? 35 : 0 },
    },
    yAxis: {
      type: 'value',
      scale: line,
      axisLabel: {
        color: '#5c6b7a',
        formatter: (value: number) => compactPublishedValue(value, input.unit),
      },
      splitLine: { lineStyle: { color: '#e7edf4' } },
    },
    series: [
      {
        name: input.seriesName,
        type: line ? 'line' : 'bar',
        data: values,
        smooth: 0.35,
        symbol: 'circle',
        symbolSize: line ? 8 : 0,
        lineStyle: { width: 3, color: '#0f766e' },
        itemStyle: { color: '#0f766e' },
        areaStyle: line ? { color: 'rgba(15, 118, 110, 0.14)' } : undefined,
        barMaxWidth: 36,
        label: {
          show: line,
          position: 'top',
          distance: 8,
          color: '#0f766e',
          fontWeight: 650,
          backgroundColor: '#ecfdf5',
          borderRadius: 8,
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
