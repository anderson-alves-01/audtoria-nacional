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
export const PUBLIC_DATA_INDICATORS = [
  'sped_quantidade_uf_cfop_ano',
  'sped_compras_uf',
  'sped_valor_estimado_uf_cfop_ano',
  'sped_valor_estimado_operacao',
  'sped_transferencias_por_direcao',
  'simulador_imposto_apurado_dados_publicos',
] as const;

/** Indicadores das aliquotas. Servem de hipotese rotulada, nunca de calculo fiscal. */
export const RATE_INDICATORS = ['icms_aliquota_ac', 'icms_aliquota_demais_uf', 'itcd_itbi_iss_aliquotas'] as const;

export const LEVEL_LABEL: Record<ReliabilityLevel, string> = {
  NAO_CONFIAVEL: 'Não confiável',
  EXPLORATORIO: 'Exploratório',
  CONFERIDO: 'Conferido',
};

/** O que falta para liberar o dado publico. Detalhes em docs/delivery/RELATORIO-SIMULADOR-SIRTA-*.md. */
export const HOMOLOGATION_NEEDS = [
  'Esclarecimento oficial do SPED sobre a definição de "Quantidade NF-e" e sobre a dimensão UF.',
  'Fonte oficial para os CFOPs 1.159, 2.159, 1.190, 2.170 e para os 5/6.15x a .19x que a tabela de CFOP não lista como transferência, e carga autorizada das transferências recebidas (1.151 a 1.154 e 2.151 a 2.154), hoje fora da planilha.',
  'Nova versão da planilha, ou regra corrigida, reconciliada com os arquivos originais.',
  'Revisão humana registrada no registro de confiabilidade, com evidência.',
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
  const found = required.map(
    (id) => block.indicators.find((indicator) => indicator.id === id) ?? missingIndicator(id),
  );
  const blocking = found.filter(
    (indicator) => indicator.level !== 'CONFERIDO' || indicator.publishableInSimulator !== true,
  );
  if (blocking.length === 0) {
    return { open: true, headline: '', blocking: [] };
  }
  const hasUnreliable = blocking.some((indicator) => indicator.level === 'NAO_CONFIAVEL');
  return {
    open: false,
    headline: hasUnreliable
      ? 'Fonte SPED NAO_CONFIAVEL: indicadores não são usados no Simulador.'
      : 'Fonte SPED EXPLORATORIO: indicadores não são publicados no Simulador até a conferência.',
    blocking,
  };
}
