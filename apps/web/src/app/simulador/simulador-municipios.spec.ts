import { MunicipalityEntry, municipalitiesOf, municipalityBelongsTo, municipalityName } from './simulador-municipios';

const CATALOG: MunicipalityEntry[] = [
  { uf: 'AC', ibge: '1200401', nome: 'Rio Branco' },
  { uf: 'AC', ibge: '1200013', nome: 'Acrelândia' },
  { uf: 'SP', ibge: '3550308', nome: 'São Paulo' },
];

describe('simulador-municipios', () => {
  it('lists nothing without a UF or without a catalog (the municipality depends on the UF)', () => {
    expect(municipalitiesOf(CATALOG, null)).toEqual([]);
    expect(municipalitiesOf(CATALOG, '')).toEqual([]);
    expect(municipalitiesOf(null, 'AC')).toEqual([]);
  });

  it('lists the municipalities of the UF in alphabetical order', () => {
    expect(municipalitiesOf(CATALOG, 'AC').map((city) => city.nome)).toEqual(['Acrelândia', 'Rio Branco']);
  });

  it('accepts only a seven-digit IBGE code that belongs to the UF', () => {
    expect(municipalityBelongsTo(CATALOG, 'AC', '1200401')).toBeTrue();
    expect(municipalityBelongsTo(CATALOG, 'SP', '1200401')).toBeFalse();
    expect(municipalityBelongsTo(CATALOG, 'AC', '12004')).toBeFalse();
    expect(municipalityBelongsTo(CATALOG, 'AC', null)).toBeFalse();
    expect(municipalityBelongsTo(CATALOG, null, '1200401')).toBeFalse();
    expect(municipalityBelongsTo(null, 'AC', '1200401')).toBeFalse();
  });

  it('names a municipality, or returns null for an unknown code', () => {
    expect(municipalityName(CATALOG, '3550308')).toBe('São Paulo');
    expect(municipalityName(CATALOG, '0000000')).toBeNull();
    expect(municipalityName(null, '3550308')).toBeNull();
  });
});
