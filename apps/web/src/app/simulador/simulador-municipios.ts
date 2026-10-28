/** Municipio da lista oficial do IBGE (referencia territorial, sem dado fiscal). */
export interface MunicipalityEntry {
  uf: string;
  ibge: string;
  nome: string;
}

export interface MunicipalityCatalog {
  fonte: string;
  obtidoEm: string;
  total: number;
  municipios: MunicipalityEntry[];
}

/** Arquivo versionado em apps/web/public, gerado por tools/ops/ibge-municipios-fetch.py. */
export const MUNICIPALITY_CATALOG_URL = '/ibge-municipios.json';

const IBGE_CODE = /^\d{7}$/;

/** Municipios de uma UF em ordem alfabetica. Sem UF, nenhum: o municipio depende da UF. */
export function municipalitiesOf(catalog: MunicipalityEntry[] | null, uf: string | null): MunicipalityEntry[] {
  if (!catalog || !uf) {
    return [];
  }
  return catalog.filter((entry) => entry.uf === uf).sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
}

/** Codigo IBGE valido e pertencente a UF. Qualquer outro valor nao vale (falha fechada). */
export function municipalityBelongsTo(
  catalog: MunicipalityEntry[] | null,
  uf: string | null,
  ibge: string | null,
): boolean {
  if (!catalog || !uf || !ibge || !IBGE_CODE.test(ibge)) {
    return false;
  }
  return catalog.some((entry) => entry.ibge === ibge && entry.uf === uf);
}

/** Nome do municipio para exibicao, ou nulo se o codigo nao estiver na lista. */
export function municipalityName(catalog: MunicipalityEntry[] | null, ibge: string | null): string | null {
  return catalog?.find((entry) => entry.ibge === ibge)?.nome ?? null;
}
