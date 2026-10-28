/**
 * Aliquotas usadas pelo Simulador. Sao parametros de simulacao, nao apuracao fiscal.
 * ITCD, ITBI e ISS tem aliquota unica informada no requisito. O ICMS e a aliquota modal
 * interna por UF do anexo fornecido pelo usuario. Aliquota ausente nunca vira zero.
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
  'Alíquotas informadas no requisito do Simulador (ITCD 6%, ITBI 3%, ISS 5%) e anexo de ICMS por UF fornecido pelo usuário em 27/10/2026. Vigência e fonte legal a confirmar.';

/** ICMS: aliquota modal interna por UF, em %. */
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

/** Aliquota em % do imposto para a UF. Sem aliquota conhecida devolve nulo (falha fechada). */
export function rateFor(tax: TaxId, uf: string | null): number | null {
  const def = TAXES.find((entry) => entry.id === tax);
  if (!def) {
    return null;
  }
  if (def.fixedRate !== null) {
    return def.fixedRate;
  }
  if (!uf) {
    return null;
  }
  return ICMS_RATE_BY_UF[uf] ?? null;
}
