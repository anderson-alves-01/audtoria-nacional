/**
 * Confiabilidade dos indicadores, no formato do bloco `reliability` da API (config/indicator-reliability.yaml).
 * Falha fechada: sem o bloco, ou com um indicador exigido ausente ou nao conferido, o dado publico
 * fica bloqueado. Nenhum codigo daqui promove um nivel: so a API, a partir do registro revisado por pessoa.
 */
export type ReliabilityLevel = 'NAO_CONFIAVEL' | 'EXPLORATORIO' | 'CONFERIDO';

export interface ReliabilityIndicator {
  id: string;
  label: string;
  level: ReliabilityLevel;
  reason: string;
  evidence: string[];
  usableForFiscalCalculation: boolean;
  publishableInSimulator: boolean;
  usableAsHypothesis: boolean;
}

export interface ReliabilityBlock {
  levels: ReliabilityLevel[];
  indicators: ReliabilityIndicator[];
}

/** Indicadores dos quais depende qualquer dado publico mostrado ou comparado no Simulador. */
export const PUBLIC_DATA_INDICATORS = ['cgu_nfe_itens_uf_ano', 'cgu_nfe_valor_itens_uf_ano'] as const;

/** Indicadores das aliquotas. Servem de hipotese rotulada, nunca de calculo fiscal. */
export const RATE_INDICATORS = ['icms_aliquota_ac', 'icms_aliquota_demais_uf', 'itcd_itbi_iss_aliquotas'] as const;

export const LEVEL_LABEL: Record<ReliabilityLevel, string> = {
  NAO_CONFIAVEL: 'Não confiável',
  EXPLORATORIO: 'Exploratório',
  CONFERIDO: 'Conferido',
};

/** O que falta para uma cobertura completa e para o imposto deixar de ser só estimativa. */
export const HOMOLOGATION_NEEDS = [
  'Sete meses de 2021 não listados no catálogo da CGU (jan–mar e mai–ago). Sem ZIP oficial a cobertura permanece PARCIAL.',
  'Homologação humana das alíquotas: o imposto do Simulador continua sendo valor × alíquota, não apuração.',
  'Não tratar a base como mercado, compras públicas totais ou NFS-e; município do emitente não é município de consumo.',
] as const;

export interface PublicGate {
  /** Verdadeiro so quando todos os indicadores exigidos estao CONFERIDO e publicaveis. */
  open: boolean;
  headline: string;
  blocking: ReliabilityIndicator[];
}

const MISSING_REASON = 'Indicador ausente da resposta da API. Tratado como NAO_CONFIAVEL (falha fechada).';

function missingIndicator(id: string): ReliabilityIndicator {
  return {
    id,
    label: id,
    level: 'NAO_CONFIAVEL',
    reason: MISSING_REASON,
    evidence: [],
    usableForFiscalCalculation: false,
    publishableInSimulator: false,
    usableAsHypothesis: false,
  };
}

export function publicDataGate(
  block: ReliabilityBlock | null | undefined,
  required: readonly string[] = PUBLIC_DATA_INDICATORS,
): PublicGate {
  if (!block || !Array.isArray(block.indicators)) {
    return {
      open: false,
      headline: 'Não foi possível verificar a confiabilidade da fonte. Os dados públicos ficam bloqueados.',
      blocking: [],
    };
  }
  // Entradas que nao sao objetos sao ignoradas, e um indicador exigido ausente conta como NAO_CONFIAVEL.
  const entries = block.indicators.filter(
    (indicator): indicator is ReliabilityIndicator => typeof indicator === 'object' && indicator !== null,
  );
  // Se o mesmo id vier mais de uma vez, todas as copias precisam passar: basta uma falhar para bloquear.
  const found = required.flatMap((id) => {
    const copies = entries.filter((indicator) => indicator.id === id);
    return copies.length > 0 ? copies : [missingIndicator(id)];
  });
  // CONFERIDO exato (sem variacao de caixa), publicavel (booleano true) e com evidencia registrada.
  const blocking = found.filter(
    (indicator) =>
      indicator.level !== 'CONFERIDO' ||
      indicator.publishableInSimulator !== true ||
      !Array.isArray(indicator.evidence) ||
      indicator.evidence.length === 0,
  );
  if (blocking.length === 0) {
    return { open: true, headline: '', blocking: [] };
  }
  const hasUnreliable = blocking.some((indicator) => indicator.level === 'NAO_CONFIAVEL');
  return {
    open: false,
    headline: hasUnreliable
      ? 'Fonte pública NAO_CONFIAVEL: indicadores não são usados no Simulador.'
      : 'Fonte pública EXPLORATORIO: indicadores não são publicados no Simulador até a conferência.',
    blocking,
  };
}
