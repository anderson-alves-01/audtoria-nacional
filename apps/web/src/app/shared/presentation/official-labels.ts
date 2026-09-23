const HOMOLOGATION: Record<string, string> = {
  REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY:
    'Validação humana concluída. O número é o valor publicado pelo órgão, só para consulta de referência. Não é crédito tributário e não autoriza cobrança, inscrição ou notificação.',
  REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION:
    'Carga técnica conferida. A validação humana ainda não foi concluída. O número permanece como referência publicada pelo órgão. Não é crédito tributário e não autoriza cobrança.',
};

const VALUE_KIND: Record<string, string> = {
  REFERENCE_QUANTITY: 'Quantidade de referência publicada pelo órgão',
  TRANSFER_AMOUNT_AS_PUBLISHED: 'Valor de transferência publicado pelo órgão',
  FISCAL_STATEMENT_LINE: 'Linha de demonstrativo fiscal publicado',
  COVERAGE_REGISTRY: 'Cadastro de cobertura, sem valor financeiro',
  CATALOG_METADATA: 'Metadado de catálogo, sem valor transferido',
  REGULATORY_DOCUMENT: 'Documento normativo, sem efeito operacional',
};

const QUALITY: Record<string, string> = {
  TECHNICALLY_VALIDATED: 'Conferido na carga técnica (checksum, esquema e contagens)',
  TECHNICALLY_APPROVED: 'Aprovado na conferência técnica do catálogo',
  PENDING_HUMAN_VALIDATION: 'Aguardando validação humana',
  COVERAGE_DIVERGENCE_PENDING_HUMAN_VALIDATION:
    'Diferença de cobertura entre as fontes, ainda sem validação humana. Não é ocorrência de cobrança.',
};

const CATALOG: Record<string, string> = {
  REFERENCE_ENRICHMENT: 'Enriquecimento de referência',
  PUBLIC_OPEN: 'Acesso público aberto',
  EMPTY: 'Sem publicação neste recorte',
};

const INDICATOR: Record<string, string> = {
  ibge_population_estimated: 'População estimada (IBGE/SIDRA 6579)',
  ibge_gdp_and_services_va: 'PIB municipal e valor adicionado de serviços (IBGE/SIDRA 5938)',
  ibge_cemp_municipal_totals: 'Cadastro Central de Empresas (IBGE/SIDRA 9509)',
  siconfi_municipal_entes: 'Cadastro de entes do SICONFI',
  siconfi_rreo: 'RREO municipal (SICONFI)',
  siconfi_dca: 'DCA/FINBRA municipal (SICONFI)',
  siconfi_rgf: 'RGF municipal (SICONFI)',
  tesouro_constitutional_transfer_types: 'Dicionário de transferências constitucionais',
  tesouro_fpm_received: 'FPM mensal publicado pelo Tesouro',
  tesouro_fpm_coint_received: 'FPM publicado pelo Tesouro (COINT)',
  fpm_published: 'FPM publicado pelo Tesouro',
  tesouro_itr_received: 'ITR mensal publicado pelo Tesouro',
  tesouro_itr_coint_received: 'ITR publicado pelo Tesouro (COINT)',
  tesouro_ipi_exp_published: 'IPI-Exportação publicado pelo Tesouro',
  tesouro_royalties_received: 'Royalties publicados pelo Tesouro',
  tesouro_lc176_received: 'LC 176/2020 publicada pelo Tesouro',
  tesouro_lc176_coint_received: 'LC 176/2020 publicada pelo Tesouro (COINT)',
  tesouro_iof_ouro_received: 'IOF-Ouro publicado pelo Tesouro',
  tesouro_iof_ouro_coint_received: 'IOF-Ouro publicado pelo Tesouro (COINT)',
  tesouro_fundeb_complement_published: 'Complementação FUNDEB publicada pelo Tesouro',
  tesouro_fundeb_received: 'FUNDEB publicado pelo Tesouro',
  tesouro_cide_received: 'CIDE-Combustíveis publicada pelo Tesouro',
  tesouro_fex_received: 'FEX publicado pelo Tesouro',
  tesouro_lc87_received: 'LC 87/96 publicada pelo Tesouro',
  regulatory_document_ec132: 'Emenda Constitucional 132/2023',
  regulatory_document_lc214: 'Lei Complementar 214/2025 (IBS/CBS)',
  estado_pe_icms_quota: 'Quota-parte de ICMS (Pernambuco)',
  estado_pe_ipva_quota: 'Quota-parte de IPVA (Pernambuco)',
  estado_pe_ipi_quota: 'Quota-parte de IPI (Pernambuco)',
  municipal_coverage_divergence: 'Divergência de cobertura municipal',
};

const SOURCE: Record<string, string> = {
  'IBGE-SIDRA': 'IBGE/SIDRA — população estimada',
  'IBGE-SIDRA-PIB': 'IBGE/SIDRA — PIB municipal',
  'IBGE-SIDRA-CEMP': 'IBGE/SIDRA — Cadastro Central de Empresas',
  'TESOURO-FPM-VALORES': 'Tesouro Nacional — FPM publicado',
  'TESOURO-ITR-VALORES': 'Tesouro Nacional — ITR publicado',
  'TESOURO-IPI-EXP-VALORES': 'Tesouro Nacional — IPI-Exportação',
  'TESOURO-ROYALTIES-VALORES': 'Tesouro Nacional — royalties',
  'TESOURO-LC176-VALORES': 'Tesouro Nacional — LC 176/2020',
  'TESOURO-IOF-OURO-VALORES': 'Tesouro Nacional — IOF-Ouro',
  'TESOURO-FUNDEB-COMPLEMENT-VALORES': 'Tesouro Nacional — complementação FUNDEB',
  'TESOURO-FUNDEB-VALORES': 'Tesouro Nacional — FUNDEB',
  'TESOURO-CIDE-VALORES': 'Tesouro Nacional — CIDE',
  'TESOURO-FEX-VALORES': 'Tesouro Nacional — FEX',
  'TESOURO-LC87-VALORES': 'Tesouro Nacional — LC 87/96',
  'TESOURO-TRANSPARENTE': 'Tesouro Nacional — dicionário de transferências',
  'SICONFI-ENTES': 'SICONFI — cadastro de entes',
  'SICONFI-RREO': 'SICONFI — RREO',
  'SICONFI-DCA': 'SICONFI — DCA',
  'SICONFI-RGF': 'SICONFI — RGF',
  'ESTADO-ICMS-QUOTA': 'Estado — quota-parte de ICMS',
  'COVERAGE-DIVERGENCE': 'Divergência de cobertura municipal',
};

const SOURCE_PART: Record<string, string> = {
  TESOURO: 'Tesouro Nacional',
  IBGE: 'IBGE',
  SIDRA: 'SIDRA',
  PIB: 'PIB',
  CEMP: 'empresas',
  SICONFI: 'SICONFI',
  RREO: 'RREO',
  DCA: 'DCA',
  RGF: 'RGF',
  ENTES: 'entes',
  FPM: 'FPM',
  ITR: 'ITR',
  IPI: 'IPI',
  EXP: 'exportação',
  ROYALTIES: 'royalties',
  FUNDEB: 'FUNDEB',
  COMPLEMENT: 'complementação',
  CIDE: 'CIDE',
  FEX: 'FEX',
  VALORES: 'valores publicados',
  TRANSPARENTE: 'dicionário',
  ESTADO: 'Estado',
  ICMS: 'ICMS',
  IPVA: 'IPVA',
  QUOTA: 'quota-parte',
  ANP: 'ANP',
  ANEEL: 'ANEEL',
  BCB: 'Banco Central',
  SGS: 'SGS',
  OLINDA: 'Olinda',
  EXPECTATIVAS: 'expectativas',
  EPE: 'EPE',
  ANATEL: 'Anatel',
  CNES: 'CNES',
  DATASUS: 'DataSUS',
  DADOS: 'dados',
  ABERTOS: 'abertos',
  REVENDEDORES: 'revendedores',
};

const WORD: Record<string, string> = {
  ibge: 'IBGE',
  gdp: 'PIB',
  and: 'e',
  services: 'de serviços',
  va: 'valor adicionado',
  population: 'população',
  estimated: 'estimada',
  municipal: 'municipal',
  coverage: 'cobertura',
  divergence: 'divergência',
  published: 'publicado',
  fpm: 'FPM',
  received: 'recebido',
  siconfi: 'SICONFI',
  rreo: 'RREO',
  dca: 'DCA',
  rgf: 'RGF',
  cemp: 'CEMP',
  totals: 'totais',
  tesouro: 'Tesouro',
};

const PROSE_REPLACEMENTS: [string, string][] = [
  ...Object.entries(HOMOLOGATION),
  ...Object.entries(VALUE_KIND),
  ...Object.entries(QUALITY),
  ...Object.entries(CATALOG),
  ...Object.entries(INDICATOR),
  ...Object.entries(SOURCE),
].sort((left, right) => right[0].length - left[0].length);

export function humanizeHomologation(status: string | null | undefined): string {
  if (!status) {
    return HOMOLOGATION['REAL_OFFICIAL_DATA_HUMAN_VALIDATED_REFERENCE_ONLY'];
  }
  return HOMOLOGATION[status] || 'Situação de validação registrada na evidência. Não é crédito tributário.';
}

export function humanizeValueKind(kind: string | null | undefined): string {
  if (!kind) {
    return 'Valor publicado pelo órgão';
  }
  return VALUE_KIND[kind] || 'Valor publicado pelo órgão';
}

export function humanizeQuality(level: string | null | undefined): string {
  if (!level) {
    return 'Qualidade não informada na carga';
  }
  return QUALITY[level] || humanizeCatalogToken(level);
}

export function humanizeCatalogToken(code: string | null | undefined): string {
  if (!code) {
    return 'não informado';
  }
  return (
    CATALOG[code] ||
    QUALITY[code] ||
    HOMOLOGATION[code] ||
    VALUE_KIND[code] ||
    'situação registrada na evidência'
  );
}

export function humanizeUnit(unit: string | null | undefined): string {
  if (unit === 'BRL') {
    return 'reais publicados pelo órgão';
  }
  if (unit === 'COUNT') {
    return 'registros na base oficial';
  }
  if (unit === 'UNIT') {
    return 'unidades publicadas pelo órgão';
  }
  if (unit === 'MIXED') {
    return 'medidas de naturezas diferentes, sem soma única';
  }
  if (unit && !/^[A-Z0-9_]+$/.test(unit)) {
    return unit;
  }
  return 'unidade publicada pelo órgão';
}

export function humanizeSource(sourceId: string | null | undefined): string {
  if (!sourceId) {
    return 'Fonte oficial';
  }
  if (SOURCE[sourceId]) {
    return SOURCE[sourceId];
  }
  if (!/^[A-Z][A-Z0-9]*(-[A-Z0-9]+)+$/.test(sourceId)) {
    return sourceId;
  }
  return sourceId
    .split('-')
    .map((part) => SOURCE_PART[part] || part)
    .join(' — ');
}

export function humanizeIndicator(indicator: string | null | undefined, presentation?: string | null): string {
  const sentence = presentation?.split('. ')[0]?.trim();
  if (sentence && !sentence.includes('_') && !sentence.startsWith('REAL_OFFICIAL')) {
    return sentence.endsWith('.') ? sentence : `${sentence}.`;
  }
  if (indicator && INDICATOR[indicator]) {
    return INDICATOR[indicator];
  }
  if (indicator?.startsWith('Cobertura ')) {
    return `Registros na base · ${humanizeSource(indicator.slice('Cobertura '.length))}`;
  }
  if (indicator && indicator.includes('_')) {
    const words = indicator
      .split('_')
      .filter((part) => part.length > 0)
      .map((part) => WORD[part] || part);
    const sentenceFromCode = words.join(' ');
    return sentenceFromCode.charAt(0).toUpperCase() + sentenceFromCode.slice(1);
  }
  return indicator || 'Indicador publicado';
}

export function humanizeProse(text: string | null | undefined): string {
  if (!text) {
    return '';
  }
  let readable = text;
  for (const [code, label] of PROSE_REPLACEMENTS) {
    if (readable.includes(code)) {
      readable = readable.split(code).join(label);
    }
  }
  return readable;
}

export function humanizeAxis(value: string): string {
  if (/^[A-Z][A-Z0-9]*(-[A-Z0-9]+)+$/.test(value)) {
    return humanizeSource(value);
  }
  return value;
}

export function humanizeSessionMode(mode: string | null | undefined): string {
  if (!mode) {
    return 'Sessão não iniciada';
  }
  if (mode === 'PUBLIC_OPEN_UI_BOOTSTRAP') {
    return 'Consulta pública de referência';
  }
  return 'Sessão autenticada';
}

export function humanizeContext(kind: 'territory' | 'purpose', id: string | null | undefined): string {
  if (!id) {
    return kind === 'territory' ? 'Território não carregado' : 'Finalidade não carregada';
  }
  if (/^[0-9a-f-]{36}$/i.test(id)) {
    return kind === 'territory'
      ? 'Território da sessão de consulta'
      : 'Finalidade de consulta pública';
  }
  return id;
}

export function formatPublishedValue(value: number | null | undefined, unit: string | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return 'Valor não publicado';
  }
  if (unit === 'BRL') {
    return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  return value.toLocaleString('pt-BR');
}

export function compactPublishedValue(value: number, unit?: string | null): string {
  if (!Number.isFinite(value)) {
    return '';
  }
  const sign = value < 0 ? '-' : '';
  const abs = Math.abs(value);
  let scaled = abs;
  let suffix = '';
  if (abs >= 1_000_000_000) {
    scaled = abs / 1_000_000_000;
    suffix = ' bi';
  } else if (abs >= 1_000_000) {
    scaled = abs / 1_000_000;
    suffix = ' mi';
  } else if (abs >= 10_000) {
    scaled = abs / 1_000;
    suffix = ' mil';
  }
  const tenths = Math.round(scaled * 10) / 10;
  const digits = suffix && tenths % 1 !== 0 ? 1 : 0;
  const text = scaled.toLocaleString('pt-BR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  if (unit === 'BRL') {
    return `${sign}R$ ${text}${suffix}`;
  }
  return `${sign}${text}${suffix}`;
}

export interface PublishedStep {
  label: string;
  value: string;
  change: string;
}

export interface PublishedSeriesReading {
  openingLabel: string;
  openingValue: string;
  closingLabel: string;
  closingValue: string;
  change: string;
  note: string;
  steps: PublishedStep[];
}

export function describePublishedSeries(
  points: { x: string; y: number }[],
  unit: string | null | undefined,
): PublishedSeriesReading | null {
  if (!points.length) {
    return null;
  }
  const steps = points.map((point, index) => {
    const previous = index > 0 ? points[index - 1] : null;
    return {
      label: point.x,
      value: withUnit(formatPublishedValue(point.y, unit), unit),
      change: previous
        ? formatPublishedChange(point.y - previous.y, previous.y, unit)
        : 'Primeiro ano publicado',
    };
  });
  const first = points[0];
  const last = points[points.length - 1];
  if (points.length === 1) {
    return {
      openingLabel: first.x,
      openingValue: withUnit(formatPublishedValue(first.y, unit), unit),
      closingLabel: '',
      closingValue: '',
      change: '',
      note: 'Somente esta competência tem valor numérico publicado nesta série.',
      steps,
    };
  }
  return {
    openingLabel: first.x,
    openingValue: withUnit(formatPublishedValue(first.y, unit), unit),
    closingLabel: last.x,
    closingValue: withUnit(formatPublishedValue(last.y, unit), unit),
    change: formatPublishedChange(last.y - first.y, first.y, unit),
    note: 'Variação entre os valores publicados no período. Não é projeção e não é crédito tributário.',
    steps,
  };
}

function withUnit(amount: string, unit: string | null | undefined): string {
  if (!unit || unit === 'BRL' || unit === 'COUNT' || unit === 'UNIT' || unit === 'MIXED') {
    return amount;
  }
  return `${amount} ${humanizeUnit(unit)}`;
}

function formatPublishedChange(
  delta: number,
  base: number,
  unit: string | null | undefined,
): string {
  const amount = formatPublishedValue(Math.abs(delta), unit);
  const signed = delta > 0 ? `+${amount}` : delta < 0 ? `-${amount}` : amount;
  if (!base) {
    return signed;
  }
  const percent = (delta / base) * 100;
  const percentText = Math.abs(percent).toLocaleString('pt-BR', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
  const percentSign = percent > 0 ? '+' : percent < 0 ? '-' : '';
  return `${signed} (${percentSign}${percentText}%)`;
}

export function publishedYearSpan(points: { x: string }[]): string {
  const years = points.map((point) => point.x).filter((label) => /^\d{4}/.test(label));
  if (years.length < 2) {
    return '';
  }
  return `${years[0]} – ${years[years.length - 1]}`;
}
