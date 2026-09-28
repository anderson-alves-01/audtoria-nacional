import { HEX_LAYOUT, HexCell } from './hex-layout';

export interface PublishedMeasure {
  sourceId?: string;
  sourceLabel?: string;
  label?: string;
  unit?: string;
  competence?: string;
  total?: number | null;
  municipalityCount?: number;
}

export interface GeographyPayload {
  regions?: {
    states?: { uf?: string; measures?: PublishedMeasure[] }[];
  }[];
}

export interface MetricPoint {
  metricId: string;
  year: string;
  value: number | null;
  unit: string;
  sourceLabel: string;
  label: string;
  municipalityCount?: number;
}

export interface AtlasState extends HexCell {
  points: MetricPoint[];
}

export interface MetricDef {
  id: string;
  label: string;
  unit: string;
  sourceLabel: string;
  ramp: string[];
}

const POP_RAMP = ['#F2E5D8', '#E4C1A8', '#D29371', '#B25F3D', '#86371C'];
const PIB_RAMP = ['#EDE7D5', '#C8D3B8', '#8FB392', '#4E7F5F', '#1B4A34'];
const CEMP_RAMP = ['#E6E9E1', '#BFCDC0', '#8FAC97', '#57836A', '#27553F'];

const ALLOWED = new Set(['IBGE-SIDRA', 'IBGE-SIDRA-PIB', 'IBGE-SIDRA-CEMP']);

/**
 * Headcount published as people becomes thousands for the template contract.
 * A unit that already says "mil" is left unchanged. Null stays null.
 */
export function populationInThousands(total: number | null | undefined, unit: string): number | null {
  if (total === null || total === undefined || Number.isNaN(Number(total))) {
    return null;
  }
  if (unit.toLowerCase().includes('mil')) {
    return Number(total);
  }
  return Number(total) / 1000;
}

function metricId(measure: PublishedMeasure): string | null {
  const source = measure.sourceId ?? '';
  if (!ALLOWED.has(source)) {
    return null;
  }
  if (source === 'IBGE-SIDRA') {
    return 'pop';
  }
  if (source === 'IBGE-SIDRA-PIB') {
    return 'pib';
  }
  const slug = (measure.label || 'cemp')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
  return `cemp:${slug || 'serie'}`;
}

function metricValue(id: string, measure: PublishedMeasure): number | null {
  if (measure.total === null || measure.total === undefined) {
    return null;
  }
  if (id === 'pop') {
    return populationInThousands(measure.total, measure.unit || '');
  }
  return Number(measure.total);
}

export function adaptGeography(payload: GeographyPayload): { states: AtlasState[]; metrics: MetricDef[] } {
  const byUf = new Map<string, MetricPoint[]>();
  const metrics = new Map<string, MetricDef>();
  for (const region of payload.regions ?? []) {
    for (const state of region.states ?? []) {
      const uf = (state.uf || '').toUpperCase();
      for (const measure of state.measures ?? []) {
        const id = metricId(measure);
        if (!id) {
          continue;
        }
        const point: MetricPoint = {
          metricId: id,
          year: String(measure.competence || '').slice(0, 4),
          value: metricValue(id, measure),
          unit: measure.unit || '',
          sourceLabel: measure.sourceLabel || '',
          label: measure.label || id,
        };
        const list = byUf.get(uf) ?? [];
        list.push(point);
        byUf.set(uf, list);
        if (!metrics.has(id)) {
          metrics.set(id, {
            id,
            label: point.label,
            unit: id === 'pop' ? 'milhares de pessoas' : id === 'pib' ? 'mil reais' : point.unit,
            sourceLabel: point.sourceLabel,
            ramp: id === 'pop' ? POP_RAMP : id === 'pib' ? PIB_RAMP : CEMP_RAMP,
          });
        }
      }
    }
  }
  const states = HEX_LAYOUT.map((cell) => ({ ...cell, points: byUf.get(cell.uf) ?? [] }));
  const order = ['pop', 'pib'];
  const defs = [...metrics.values()].sort((a, b) => {
    const ia = order.indexOf(a.id);
    const ib = order.indexOf(b.id);
    return (ia === -1 ? 9 : ia) - (ib === -1 ? 9 : ib) || a.label.localeCompare(b.label, 'pt-BR');
  });
  return { states, metrics: defs };
}

const MONEY_ALLOWED = new Set(['TESOURO-FPM-VALORES', 'SICONFI-RREO', 'SICONFI-DCA']);
const MONEY_ORDER = ['TESOURO-FPM-VALORES', 'SICONFI-RREO', 'SICONFI-DCA'];

/** Published reais stay in reais. Population and PIB series are left to the executive map. */
export function adaptMoneyGeography(payload: GeographyPayload): { states: AtlasState[]; metrics: MetricDef[] } {
  const byUf = new Map<string, MetricPoint[]>();
  const metrics = new Map<string, MetricDef>();
  for (const region of payload.regions ?? []) {
    for (const state of region.states ?? []) {
      const uf = (state.uf || '').toUpperCase();
      for (const measure of state.measures ?? []) {
        const id = measure.sourceId ?? '';
        if (!MONEY_ALLOWED.has(id) || measure.total === null || measure.total === undefined) {
          continue;
        }
        const point: MetricPoint = {
          metricId: id,
          year: String(measure.competence || '').slice(0, 4),
          value: Number(measure.total),
          unit: 'reais',
          sourceLabel: measure.sourceLabel || measure.label || id,
          label: measure.label || measure.sourceLabel || id,
          municipalityCount: measure.municipalityCount,
        };
        const list = byUf.get(uf) ?? [];
        list.push(point);
        byUf.set(uf, list);
        if (!metrics.has(id)) {
          metrics.set(id, {
            id,
            label: point.label,
            unit: 'reais',
            sourceLabel: point.sourceLabel,
            ramp: PIB_RAMP,
          });
        }
      }
    }
  }
  const states = HEX_LAYOUT.map((cell) => ({ ...cell, points: byUf.get(cell.uf) ?? [] }));
  const defs = [...metrics.values()].sort(
    (a, b) => MONEY_ORDER.indexOf(a.id) - MONEY_ORDER.indexOf(b.id),
  );
  return { states, metrics: defs };
}

export function formatPublishedReais(value: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '—';
  }
  const abs = Math.abs(value);
  const compact = (divisor: number, suffix: string) =>
    `${(value / divisor).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} ${suffix}`;
  if (abs >= 1_000_000_000_000) {
    return compact(1_000_000_000_000, 'tri');
  }
  if (abs >= 1_000_000_000) {
    return compact(1_000_000_000, 'bi');
  }
  if (abs >= 1_000_000) {
    return compact(1_000_000, 'mi');
  }
  return `${value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} reais`;
}

export function valueAt(state: AtlasState, metricId: string, year: string): number | null {
  const point = state.points.find((item) => item.metricId === metricId && item.year === year);
  return point ? point.value : null;
}

export function yearsFor(states: AtlasState[], metricId: string): string[] {
  const years = new Set<string>();
  for (const state of states) {
    for (const point of state.points) {
      if (point.metricId === metricId && point.year && point.value !== null) {
        years.add(point.year);
      }
    }
  }
  return [...years].sort((a, b) => a.localeCompare(b));
}

export function foldYear(text: string): string {
  return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

export function formatMetric(metric: MetricDef | undefined, value: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '—';
  }
  if (!metric) {
    return value.toLocaleString('pt-BR');
  }
  if (metric.id === 'pop') {
    return value >= 1000
      ? `${(value / 1000).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} mi`
      : `${Math.round(value).toLocaleString('pt-BR')} mil`;
  }
  if (metric.id === 'pib') {
    return `${value.toLocaleString('pt-BR', { maximumFractionDigits: 1 })} mil reais`;
  }
  return `${value.toLocaleString('pt-BR')} ${metric.unit}`.trim();
}

export function quantileFill(value: number | null, samples: number[], ramp: string[]): string | null {
  if (value === null || !samples.length) {
    return null;
  }
  const sorted = [...samples].sort((a, b) => a - b);
  const at = (portion: number) => sorted[Math.floor(portion * (sorted.length - 1))];
  const cuts = [0.2, 0.4, 0.6, 0.8].map(at);
  let band = 0;
  for (const cut of cuts) {
    if (value > cut) {
      band += 1;
    }
  }
  return ramp[band] ?? ramp[ramp.length - 1];
}

export function textOn(fill: string): string {
  const hex = fill.replace('#', '');
  const n = Number.parseInt(hex, 16);
  const luminance = 0.2126 * ((n >> 16) & 255) + 0.7152 * ((n >> 8) & 255) + 0.0722 * (n & 255);
  return luminance < 145 ? '#F4F0E5' : '#1A1913';
}
