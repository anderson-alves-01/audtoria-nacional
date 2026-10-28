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
    evidence: level === 'CONFERIDO' ? ['evidence/ops/exemplo.md'] : [],
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
  describe('tampered or inconsistent answers (anti-circumvention)', () => {
    const first = PUBLIC_DATA_INDICATORS[0];

    it('stays closed when the same indicator appears twice and one copy is not CONFERIDO', () => {
      const conferidoFirst = block('CONFERIDO');
      conferidoFirst.indicators.push(indicator(first, 'NAO_CONFIAVEL'));
      expect(publicDataGate(conferidoFirst).open).toBeFalse();
      const conferidoLast = block('CONFERIDO');
      conferidoLast.indicators.unshift(indicator(first, 'EXPLORATORIO'));
      expect(publicDataGate(conferidoLast).open).toBeFalse();
    });

    it('stays closed for CONFERIDO without any evidence', () => {
      const bare = block('CONFERIDO');
      bare.indicators[0] = { ...indicator(first, 'CONFERIDO'), evidence: [] };
      const gate = publicDataGate(bare);
      expect(gate.open).toBeFalse();
      expect(gate.blocking.map((item) => item.id)).toEqual([first]);
    });

    it('stays closed for an unknown, lower-case or empty level', () => {
      for (const level of ['OUTRO', 'conferido', 'Conferido', '', ' CONFERIDO']) {
        const odd = block('CONFERIDO');
        odd.indicators[0] = { ...indicator(first, 'CONFERIDO'), level: level as ReliabilityLevel };
        expect(publicDataGate(odd).open).withContext(level).toBeFalse();
      }
    });

    it('stays closed when publishable is anything but the boolean true', () => {
      for (const flag of [undefined, null, 'true', 1, 0, false]) {
        const odd = block('CONFERIDO');
        odd.indicators[0] = {
          ...indicator(first, 'CONFERIDO'),
          publishableInSimulator: flag as unknown as boolean,
        };
        expect(publicDataGate(odd).open).withContext(String(flag)).toBeFalse();
      }
    });

    it('ignores a publishable flag on an indicator that is not CONFERIDO', () => {
      const odd = block('CONFERIDO');
      odd.indicators[0] = indicator(first, 'EXPLORATORIO', true);
      expect(publicDataGate(odd).open).toBeFalse();
      odd.indicators[0] = indicator(first, 'NAO_CONFIAVEL', true);
      expect(publicDataGate(odd).open).toBeFalse();
    });

    it('does not let an extra CONFERIDO indicator stand in for a required one', () => {
      const extra = block('CONFERIDO');
      extra.indicators = [...extra.indicators.slice(1), indicator('qualquer_outro', 'CONFERIDO')];
      expect(publicDataGate(extra).open).toBeFalse();
    });

    it('stays closed for entries that are not objects', () => {
      const broken = block('CONFERIDO');
      broken.indicators[0] = null as unknown as ReliabilityIndicator;
      expect(publicDataGate(broken).open).toBeFalse();
    });
  });});
