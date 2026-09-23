import { buildChartOptions } from './chart-options';

describe('chart options', () => {
  it('draws a labeled line with the published years and keeps mil reais unlabeled as currency', () => {
    const options = buildChartOptions({
      chartType: 'line',
      seriesName: 'PIB',
      unit: 'Mil Reais',
      points: [
        { x: '2021', y: 9012142031 },
        { x: '2022', y: 10079676379 },
        { x: '2023', y: 10943345420 },
      ],
    });
    const series = options.series as { type: string; areaStyle?: object; label?: { show?: boolean } }[];
    expect(series[0].type).toBe('line');
    expect(series[0].areaStyle).toBeTruthy();
    expect(series[0].label?.show).toBeTrue();
    const axis = options.yAxis as { axisLabel?: { formatter?: (value: number) => string } };
    expect(axis.axisLabel?.formatter?.(10943345420)).toBe('10,9 bi');
    expect(axis.axisLabel?.formatter?.(10943345420)).not.toContain('R$');
  });

  it('keeps a single-competence chart as a bar without a point label', () => {
    const options = buildChartOptions({
      chartType: 'bar',
      seriesName: 'Cobertura',
      unit: 'COUNT',
      points: [{ x: 'IBGE', y: 5570 }],
    });
    const series = options.series as { type: string; label?: { show?: boolean } }[];
    expect(series[0].type).toBe('bar');
    expect(series[0].label?.show).toBeFalse();
  });
});
