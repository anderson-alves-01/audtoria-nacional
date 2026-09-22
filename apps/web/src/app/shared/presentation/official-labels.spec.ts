import {
  formatPublishedValue,
  humanizeHomologation,
  humanizeIndicator,
  humanizeSource,
  humanizeValueKind,
} from './official-labels';

describe('official labels', () => {
  it('explains validation and measure without internal codes', () => {
    expect(humanizeHomologation('REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY')).toContain(
      'Não é crédito tributário',
    );
    expect(humanizeHomologation('REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY')).not.toContain(
      'REAL_OFFICIAL',
    );
    expect(humanizeValueKind('REFERENCE_QUANTITY')).toBe('Quantidade de referência publicada pelo órgão');
    expect(humanizeIndicator('ibge_gdp_and_services_va')).toBe(
      'PIB municipal e valor adicionado de serviços (IBGE/SIDRA 5938)',
    );
    expect(humanizeIndicator('ibge_population_estimated', 'População estimada publicada pelo IBGE. Não é crédito.')).toBe(
      'População estimada publicada pelo IBGE.',
    );
    expect(humanizeSource('TESOURO-FPM-VALORES')).toBe('Tesouro Nacional — FPM publicado');
    expect(formatPublishedValue(1000, 'BRL')).toContain('R$');
    expect(formatPublishedValue(18642470, 'UNIT')).not.toContain('R$');
  });
});
