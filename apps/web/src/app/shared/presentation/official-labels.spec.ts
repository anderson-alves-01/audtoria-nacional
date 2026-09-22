import {
  formatPublishedValue,
  humanizeContext,
  humanizeHomologation,
  humanizeIndicator,
  humanizeQuality,
  humanizeSessionMode,
  humanizeSource,
  humanizeUnit,
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
    expect(humanizeUnit('Pessoas')).toBe('Pessoas');
    expect(humanizeSessionMode('PUBLIC_OPEN_UI_BOOTSTRAP')).toBe('Consulta pública de referência');
    expect(humanizeSessionMode('PUBLIC_OPEN_UI_BOOTSTRAP')).not.toContain('PUBLIC_OPEN');
    expect(humanizeContext('territory', '11111111-1111-4111-8111-111111111021')).toBe(
      'Território da sessão de consulta',
    );
    expect(humanizeQuality('COVERAGE_DIVERGENCE_PENDING_HUMAN_VALIDATION')).toContain(
      'Diferença de cobertura',
    );
  });
});
