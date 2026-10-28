/**
 * Aliquotas usadas pelo Simulador. Sao parametros de simulacao, nao apuracao fiscal.
 * As aliquotas vem de /v1/tax-rates, versionadas por vigencia, com status VALIDADO (base legal
 * registrada) ou PENDENTE (sem validacao juridica). As tabelas ICMS_RATE_BY_UF e FLAT_RATES abaixo
 * sao so o reserva quando a leitura falha e entram sempre como PENDENTE. Aliquota ausente nunca
 * vira zero. ICMS e a aliquota modal: excecoes por mercadoria e operacao nao estao modeladas.
 */
export type TaxId = 'ITCD' | 'ITBI' | 'ISS' | 'ICMS';

export interface TaxDef {
  id: TaxId;
  label: string;
  /** Aliquota unica em %. Nulo quando depende da UF. */
  fixedRate: number | null;
}

export const TAXES: TaxDef[] = [
  { id: 'ITCD', label: 'ITCD', fixedRate: 6 },
  { id: 'ITBI', label: 'ITBI', fixedRate: 3 },
  { id: 'ISS', label: 'ISS', fixedRate: 5 },
  { id: 'ICMS', label: 'ICMS (por UF)', fixedRate: null },
];

export const RATE_SOURCE =
  'Alíquotas lidas da tabela versionada por vigência. Só as marcadas Validado têm base legal registrada (hoje, o ICMS modal do Acre, com a documentação jurídica completa mas ainda sem homologação do responsável). As demais estão Pendentes de validação jurídica e não devem ser tratadas como validadas. Percentuais lidos de uma imagem não são fundamento legal: nenhuma tabela está homologada. ITCD (estadual), ITBI e ISS (municipais) usam parâmetros de simulação; uma alíquota única não vale para todas as UFs nem para todos os municípios.';

export const RATE_CAVEAT =
  'Alíquota modal: exceções por mercadoria e operação não estão modeladas.';

/** Reserva: ICMS modal interna por UF (anexo enviado pelo usuario), sempre PENDENTE. */
export const ICMS_RATE_BY_UF: Record<string, number> = {
  AC: 19,
  AL: 20.5,
  AP: 18,
  AM: 20,
  BA: 20.5,
  CE: 20,
  DF: 20,
  ES: 17,
  GO: 19,
  MA: 23,
  MT: 17,
  MS: 17,
  MG: 18,
  PA: 19,
  PB: 20,
  PR: 19.5,
  PE: 20.5,
  PI: 22.5,
  RJ: 20,
  RN: 20,
  RS: 17,
  RO: 19.5,
  RR: 20,
  SC: 17,
  SP: 18,
  SE: 19,
  TO: 20,
};

/** Tipos de bem e servico. Rotulo do cenario simulado: o dado publico nao traz essa dimensao. */
export const GOODS_TYPES = [
  'Veículos',
  'Imóveis',
  'Eletrodomésticos',
  'Alimentos e Bebidas',
  'Outros Bens',
  'Serviços Gerais',
] as const;

/**
 * Operacoes e anos do contrato SPED-NFE-UF-CFOP. Servem de lista quando a leitura do dado
 * publico falha ou nao ha carga: o simulador continua utilizavel sem inventar numero.
 */
export const SPED_OPERATIONS = [
  'Compras',
  'Vendas',
  'Transferências',
  'Doações / bonificações / brindes',
  'Serviços Prestados',
  'Serviços Tomados',
  'Outras Saídas',
] as const;

export const SPED_YEARS = [2021, 2022, 2023, 2024, 2025] as const;

export type RateStatus = 'VALIDADO' | 'PENDENTE';

/** Versao de aliquota no formato de /v1/tax-rates. Data nula significa desconhecida ou aberta. */
export interface RateVersion {
  tax: TaxId;
  uf: string;
  rateKind: string;
  rate: number;
  validFrom: string | null;
  validTo: string | null;
  legalBasis: string | null;
  officialUrl: string | null;
  status: RateStatus | 'REVOGADO';
  note: string | null;
  /** UF, MUNICIPIO ou SIMULACAO. Ausente em respostas antigas: uf BR conta como simulacao. */
  jurisdictionLevel?: 'UF' | 'MUNICIPIO' | 'SIMULACAO';
  isSimulationParameter?: boolean;
  municipalityIbgeCode?: string | null;
  operationRef?: string | null;
}

export interface ResolvedRate {
  rate: number | null;
  status: RateStatus | null;
  /** A aliquota validada mudou dentro do ano: nao existe taxa anual unica. */
  changedWithinYear: boolean;
  version: RateVersion | null;
  /** Parametro de simulacao: nao e a aliquota de nenhuma UF nem municipio. */
  isSimulation: boolean;
}

export const NO_RATE: ResolvedRate = {
  rate: null,
  status: null,
  changedWithinYear: false,
  version: null,
  isSimulation: false,
};

const FLAT_UF = 'BR';
const USABLE_KINDS = ['MODAL', 'UNICA'];

/** Reserva quando /v1/tax-rates falha: tudo PENDENTE, sem data, sem base legal. */
export function fallbackVersions(): RateVersion[] {
  const base = { validFrom: null, validTo: null, legalBasis: null, officialUrl: null, status: 'PENDENTE' as const };
  const flat = TAXES.filter((def) => def.fixedRate !== null).map<RateVersion>((def) => ({
    ...base,
    tax: def.id,
    uf: FLAT_UF,
    rateKind: 'UNICA',
    jurisdictionLevel: 'SIMULACAO',
    rate: def.fixedRate as number,
    note: 'Reserva local; leitura da tabela versionada indisponível.',
  }));
  const icms = Object.entries(ICMS_RATE_BY_UF).map<RateVersion>(([uf, rate]) => ({
    ...base,
    tax: 'ICMS',
    uf,
    rateKind: 'MODAL',
    rate,
    note: 'Reserva local; leitura da tabela versionada indisponível.',
  }));
  return [...flat, ...icms];
}

function levelOf(version: RateVersion): 'UF' | 'MUNICIPIO' | 'SIMULACAO' {
  return version.jurisdictionLevel ?? (version.uf === FLAT_UF ? 'SIMULACAO' : 'UF');
}

/**
 * ITBI e ISS sao municipais: sem municipio na escolha, so o parametro de simulacao serve. ITCD e
 * estadual: uma linha da UF vence o parametro. Linha de municipio so casa com o codigo IBGE escolhido, nunca so pela UF.
 */
function matches(version: RateVersion, tax: TaxId, uf: string | null, municipality: string | null): boolean {
  if (version.status === 'REVOGADO' || version.tax !== tax || !USABLE_KINDS.includes(version.rateKind)) {
    return false;
  }
  if (version.operationRef) {
    return false;
  }
  const level = levelOf(version);
  if (level === 'SIMULACAO') {
    return tax !== 'ICMS' && version.uf === FLAT_UF;
  }
  if (level === 'MUNICIPIO') {
    return (tax === 'ITBI' || tax === 'ISS') && municipality !== null && version.municipalityIbgeCode === municipality;
  }
  return (tax === 'ICMS' || tax === 'ITCD') && uf !== null && version.uf === uf;
}

function overlaps(version: RateVersion, start: string, end: string): boolean {
  if (version.validFrom !== null && version.validFrom > end) {
    return false;
  }
  return !(version.validTo !== null && version.validTo < start);
}

/**
 * Aliquota do imposto para a UF no ano. Validada vence pendente. Se a aliquota validada muda
 * dentro do ano, nao ha taxa anual: devolve nulo com changedWithinYear. Sem aliquota, nulo.
 */
export function resolveRate(
  versions: RateVersion[],
  tax: TaxId,
  uf: string | null,
  year: number,
  municipality: string | null = null,
): ResolvedRate {
  const start = `${year}-01-01`;
  const end = `${year}-12-31`;
  const found = versions.filter((version) => matches(version, tax, uf, municipality) && overlaps(version, start, end));
  if (found.length === 0) {
    return NO_RATE;
  }
  // A aliquota de uma jurisdicao real vence o parametro de simulacao.
  const real = found.filter((version) => levelOf(version) !== 'SIMULACAO');
  const pool = real.length > 0 ? real : found;
  const validated = pool.filter((version) => version.status === 'VALIDADO');
  const chosen = validated.length > 0 ? validated : pool;
  const status = chosen[0].status as RateStatus;
  const isSimulation = levelOf(chosen[0]) === 'SIMULACAO';
  if (new Set(chosen.map((version) => version.rate)).size > 1) {
    return { rate: null, status, changedWithinYear: true, version: null, isSimulation };
  }
  const best = [...chosen].sort((a, b) => (b.validFrom ?? '').localeCompare(a.validFrom ?? ''))[0];
  return { rate: best.rate, status, changedWithinYear: false, version: best, isSimulation };
}

/** Texto do selo de uma aliquota. */
export function rateStatusLabel(status: RateStatus | null): string {
  if (status === 'VALIDADO') {
    return 'Validado';
  }
  return status === 'PENDENTE' ? 'Pendente de validação jurídica' : '';
}
