/** Cartographic constants from the Atlas template. Not an official series. */

export type AtlasRegion = 'N' | 'NE' | 'CO' | 'SE' | 'S';

export interface HexCell {
  uf: string;
  nome: string;
  reg: AtlasRegion;
  col: number;
  row: number;
}

export const REGION_COLOR: Record<AtlasRegion, string> = {
  N: '#2D6A4F',
  NE: '#C2542E',
  CO: '#B98A2F',
  SE: '#8C3B4A',
  S: '#3E6B72',
};

export const REGION_NAME: Record<AtlasRegion, string> = {
  N: 'Norte',
  NE: 'Nordeste',
  CO: 'Centro-Oeste',
  SE: 'Sudeste',
  S: 'Sul',
};

export const REGION_LABELS = [
  { t: 'NORTE', x: 177, y: -46 },
  { t: 'NORDESTE', x: 443, y: 100 },
  { t: 'CENTRO-OESTE', x: 100, y: 151 },
  { t: 'SUDESTE', x: 448, y: 258 },
  { t: 'SUL', x: 95, y: 357 },
];

/** col/row kept exactly as in template/index.html. Capitals are not included. */
export const HEX_LAYOUT: HexCell[] = [
  { uf: 'AC', nome: 'Acre', reg: 'N', col: 0, row: 2 },
  { uf: 'AL', nome: 'Alagoas', reg: 'NE', col: 6, row: 4 },
  { uf: 'AP', nome: 'Amapá', reg: 'N', col: 4, row: 0 },
  { uf: 'AM', nome: 'Amazonas', reg: 'N', col: 1, row: 1 },
  { uf: 'BA', nome: 'Bahia', reg: 'NE', col: 4, row: 3 },
  { uf: 'CE', nome: 'Ceará', reg: 'NE', col: 5, row: 2 },
  { uf: 'DF', nome: 'Distrito Federal', reg: 'CO', col: 4, row: 4 },
  { uf: 'ES', nome: 'Espírito Santo', reg: 'SE', col: 5, row: 5 },
  { uf: 'GO', nome: 'Goiás', reg: 'CO', col: 3, row: 4 },
  { uf: 'MA', nome: 'Maranhão', reg: 'NE', col: 4, row: 1 },
  { uf: 'MT', nome: 'Mato Grosso', reg: 'CO', col: 3, row: 3 },
  { uf: 'MS', nome: 'Mato Grosso do Sul', reg: 'CO', col: 2, row: 4 },
  { uf: 'MG', nome: 'Minas Gerais', reg: 'SE', col: 5, row: 4 },
  { uf: 'PA', nome: 'Pará', reg: 'N', col: 3, row: 1 },
  { uf: 'PB', nome: 'Paraíba', reg: 'NE', col: 6, row: 3 },
  { uf: 'PR', nome: 'Paraná', reg: 'S', col: 3, row: 6 },
  { uf: 'PE', nome: 'Pernambuco', reg: 'NE', col: 5, row: 3 },
  { uf: 'PI', nome: 'Piauí', reg: 'NE', col: 4, row: 2 },
  { uf: 'RJ', nome: 'Rio de Janeiro', reg: 'SE', col: 4, row: 5 },
  { uf: 'RN', nome: 'Rio Grande do Norte', reg: 'NE', col: 6, row: 2 },
  { uf: 'RS', nome: 'Rio Grande do Sul', reg: 'S', col: 2, row: 8 },
  { uf: 'RO', nome: 'Rondônia', reg: 'N', col: 2, row: 2 },
  { uf: 'RR', nome: 'Roraima', reg: 'N', col: 2, row: 0 },
  { uf: 'SC', nome: 'Santa Catarina', reg: 'S', col: 3, row: 7 },
  { uf: 'SP', nome: 'São Paulo', reg: 'SE', col: 3, row: 5 },
  { uf: 'SE', nome: 'Sergipe', reg: 'NE', col: 6, row: 5 },
  { uf: 'TO', nome: 'Tocantins', reg: 'N', col: 3, row: 2 },
];
