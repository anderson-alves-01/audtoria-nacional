import {
  PUBLIC_DATA_INDICATORS,
  ReliabilityBlock,
  ReliabilityIndicator,
  ReliabilityLevel,
  publicDataGate,
} from './indicator-reliability';

function indicator(id: string, level: ReliabilityLevel, publishable = level === 'CONFERIDO'): ReliabilityIndicator {
  return {
    id,
    label: id,
    level,
    reason: 'r',
    evidence: [],
    usableForFiscalCalculation: level === 'CONFERIDO',
    publishableInSimulator: publishable,
    usableAsHypothesis: level !== 'NAO_CONFIAVEL',
  };
}

function block(level: ReliabilityLevel): ReliabilityBlock {
  return {
    levels: ['NAO_CONFIAVEL', 'EXPLORATORIO', 'CONFERIDO'],
    indicators: PUBLIC_DATA_INDICATORS.map((id) => indicator(id, level)),
  };
}

describe('publicDataGate', () => {
  it('stays closed with no block at all (fail closed)', () => {
    expect(publicDataGate(null).open).toBeFalse();
    expect(publicDataGate(undefined).open).toBeFalse();
    expect(publicDataGate({ levels: [], indicators: 'x' as unknown as ReliabilityIndicator[] }).open).toBeFalse();
  });

  it('stays closed for NAO_CONFIAVEL and names every blocking indicator', () => {
    const gate = publicDataGate(block('NAO_CONFIAVEL'));
    expect(gate.open).toBeFalse();
    expect(gate.headline).toContain('NAO_CONFIAVEL');
    expect(gate.blocking.length).toBe(PUBLIC_DATA_INDICATORS.length);
  });

  it('stays closed for EXPLORATORIO', () => {
    const gate = publicDataGate(block('EXPLORATORIO'));
    expect(gate.open).toBeFalse();
    expect(gate.headline).toContain('EXPLORATORIO');
  });

  it('stays closed when the level says CONFERIDO but the API did not mark it publishable', () => {
    const odd = block('CONFERIDO');
    odd.indicators[0] = indicator(PUBLIC_DATA_INDICATORS[0], 'CONFERIDO', false);
    expect(publicDataGate(odd).open).toBeFalse();
  });

  it('treats a missing required indicator as NAO_CONFIAVEL', () => {
    const partial = block('CONFERIDO');
    partial.indicators = partial.indicators.slice(1);
    const gate = publicDataGate(partial);
    expect(gate.open).toBeFalse();
    expect(gate.blocking[0].id).toBe(PUBLIC_DATA_INDICATORS[0]);
    expect(gate.blocking[0].level).toBe('NAO_CONFIAVEL');
  });

  it('opens only when every required indicator is CONFERIDO and publishable', () => {
    expect(publicDataGate(block('CONFERIDO')).open).toBeTrue();
  });
});
