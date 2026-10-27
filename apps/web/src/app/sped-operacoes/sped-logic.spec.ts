import { HEX_LAYOUT } from '../atlas/hex-layout';
import {
  SpedSerieItem,
  bounds,
  byOperation,
  byUf,
  byYear,
  formatMeasure,
  hexShapes,
  intensity,
  money,
  sumKnown,
} from './sped-logic';

const items: SpedSerieItem[] = [
  { ano: 2021, uf: 'SP', operacao: 'Vendas', quantidade: 10, valorEstimado: '100.50' },
  { ano: 2022, uf: 'SP', operacao: 'Vendas', quantidade: 20, valorEstimado: '200.00' },
  { ano: 2021, uf: 'SP', operacao: 'Compras', quantidade: 5, valorEstimado: '50.00' },
  { ano: 2021, uf: 'AC', operacao: 'Serviços Prestados', quantidade: 0, valorEstimado: null },
];

describe('sped logic', () => {
  it('keeps a missing value empty and never turns it into zero', () => {
    expect(money(null)).toBeNull();
    expect(money('')).toBeNull();
    expect(formatMeasure(null, 'valor')).toBe('—');
    expect(sumKnown([null, null])).toBeNull();
    expect(sumKnown([null, 3])).toBe(3);
  });

  it('sums years inside one operation and leaves UFs without rows empty', () => {
    const map = byUf(items, 'Vendas', 'quantidade', null);
    expect(map.get('SP')).toBe(30);
    expect(map.get('AC')).toBeNull();
    expect(byUf(items, 'Vendas', 'valor', '2021').get('SP')).toBe(100.5);
    expect(byUf(items, 'Serviços Prestados', 'valor', null).get('AC')).toBeNull();
    expect(byUf(items, 'Serviços Prestados', 'quantidade', null).get('AC')).toBe(0);
  });

  it('gives one value per operation and no cross-operation total', () => {
    const map = byOperation(items, ['Vendas', 'Compras', 'Doações / bonificações / brindes'], 'quantidade', {
      ano: null,
      uf: 'SP',
    });
    expect([...map.entries()]).toEqual([
      ['Vendas', 30],
      ['Compras', 5],
      ['Doações / bonificações / brindes', null],
    ]);
  });

  it('builds the yearly line with gaps for years without rows', () => {
    expect(byYear(items, [2021, 2022, 2023], 'Vendas', 'quantidade', 'SP')).toEqual([10, 20, null]);
  });

  it('keeps the template hexagon coordinates for the 27 UFs', () => {
    const shapes = hexShapes();
    expect(shapes.length).toBe(27);
    expect(shapes.length).toBe(HEX_LAYOUT.length);
    const sp = shapes.find((shape) => shape.cell.uf === 'SP');
    expect(sp?.cell.col).toBe(3);
    expect(sp?.cell.row).toBe(5);
    expect(new Set(shapes.map((shape) => `${shape.cx.toFixed(1)}|${shape.cy.toFixed(1)}`)).size).toBe(27);
  });

  it('scales intensity only between existing values', () => {
    expect(bounds([null, 2, 10])).toEqual({ min: 2, max: 10 });
    expect(bounds([null])).toBeNull();
    expect(intensity(null, 0, 10)).toBeNull();
    expect(intensity(5, 0, 10)).toBe(0.5);
    expect(intensity(5, 5, 5)).toBe(1);
  });
});
