import {
  adaptGeography,
  adaptMoneyGeography,
  formatMetric,
  formatPublishedReais,
  populationInThousands,
  quantileFill,
} from './geography-adapter';

describe('adaptGeography', () => {
  it('puts Acre population in thousands and keeps PIB in published mil reais', () => {
    const view = adaptGeography({
      regions: [
        {
          states: [
            {
              uf: 'AC',
              measures: [
                {
                  sourceId: 'IBGE-SIDRA',
                  sourceLabel: 'IBGE — população',
                  label: 'População residente estimada',
                  unit: 'Pessoas',
                  competence: '2024',
                  total: 830000,
                  municipalityCount: 22,
                },
                {
                  sourceId: 'IBGE-SIDRA-PIB',
                  sourceLabel: 'IBGE — PIB',
                  label: 'PIB',
                  unit: 'Mil Reais',
                  competence: '2021',
                  total: 21000,
                  municipalityCount: 22,
                },
              ],
            },
          ],
        },
      ],
    });
    const acre = view.states.find((state) => state.uf === 'AC');
    expect(acre?.reg).toBe('N');
    expect(acre?.points.find((point) => point.metricId === 'pop')?.value).toBe(830);
    expect(acre?.points.find((point) => point.metricId === 'pib')?.value).toBe(21000);
    expect(view.metrics.map((metric) => metric.id)).toEqual(['pop', 'pib']);
    expect(view.states.find((state) => state.uf === 'SP')?.points).toEqual([]);
  });

  it('keeps a missing total as null and drops it from the color scale', () => {
    expect(populationInThousands(null, 'Pessoas')).toBeNull();
    const metric = { id: 'pib', label: 'PIB', unit: 'mil reais', sourceLabel: '', ramp: ['#111'] };
    expect(formatMetric(metric, null)).toBe('—');
    expect(quantileFill(null, [1, 2, 3], ['#111', '#222'])).toBeNull();
  });
});

describe('adaptMoneyGeography', () => {
  it('keeps the published reais and ignores population', () => {
    const view = adaptMoneyGeography({
      regions: [
        {
          states: [
            {
              uf: 'AC',
              measures: [
                {
                  sourceId: 'TESOURO-FPM-VALORES',
                  label: 'FPM publicado',
                  sourceLabel: 'FPM publicado',
                  unit: 'BRL',
                  competence: '2025',
                  total: 2_500_000,
                  municipalityCount: 22,
                },
                {
                  sourceId: 'IBGE-SIDRA',
                  label: 'População',
                  unit: 'Pessoas',
                  competence: '2024',
                  total: 830000,
                },
              ],
            },
          ],
        },
      ],
    });
    const acre = view.states.find((state) => state.uf === 'AC');
    expect(acre?.points).toEqual([
      jasmine.objectContaining({ metricId: 'TESOURO-FPM-VALORES', value: 2_500_000, municipalityCount: 22 }),
    ]);
    expect(view.metrics.map((metric) => metric.id)).toEqual(['TESOURO-FPM-VALORES']);
    expect(formatPublishedReais(2_500_000)).toBe('2,5 mi');
    expect(formatPublishedReais(null)).toBe('—');
  });
});
