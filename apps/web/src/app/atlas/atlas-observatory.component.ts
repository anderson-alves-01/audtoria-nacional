import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import {
  AfterViewChecked,
  Component,
  ElementRef,
  HostListener,
  OnInit,
  QueryList,
  ViewChild,
  ViewChildren,
  inject,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  AtlasState,
  GeographyPayload,
  MetricDef,
  adaptGeography,
  foldYear,
  formatMetric,
  quantileFill,
  textOn,
  valueAt,
  yearsFor,
} from './geography-adapter';
import { REGION_COLOR, REGION_LABELS, REGION_NAME } from './hex-layout';

const SVGNS = 'http://www.w3.org/2000/svg';
const HR = 34;

type TabId = 'visao' | 'mapa' | 'rankings' | 'comparar' | 'metodo';

@Component({
  selector: 'app-atlas-observatory',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './atlas-observatory.component.html',
})
export class AtlasObservatoryComponent implements OnInit, AfterViewChecked {
  private readonly http = inject(HttpClient);

  @ViewChild('hexmap') hexmap?: ElementRef<SVGSVGElement>;
  @ViewChild('lineChart') lineChart?: ElementRef<SVGSVGElement>;
  @ViewChildren('tabBtn') tabButtons?: QueryList<ElementRef<HTMLButtonElement>>;

  tab: TabId = 'visao';
  indicatorLeft = 0;
  indicatorWidth = 0;
  loading = true;
  failed = false;
  states: AtlasState[] = [];
  metrics: MetricDef[] = [];
  metricId = '';
  year = '';
  query = '';
  sortId = 'nome';
  sortDesc = false;
  drawer: AtlasState | null = null;
  compared: string[] = [];
  toast = '';
  flashUf = '';
  lineTip = '';
  kpiDisplay: string[] = ['—', '—', '—', '—'];
  private drawQueued = false;
  private kpiToken = 0;

  ngOnInit(): void {
    this.http.get<GeographyPayload>('/v1/dashboards/executivo/geography').subscribe({
      next: (payload) => {
        const adapted = adaptGeography(payload);
        this.states = adapted.states;
        this.metrics = adapted.metrics;
        this.metricId = this.metrics[0]?.id ?? '';
        this.year = this.years().at(-1) ?? '';
        this.loading = false;
        this.queueDraw();
        this.refreshKpis();
      },
      error: (_error: HttpErrorResponse) => {
        this.failed = true;
        this.loading = false;
        this.states = adaptGeography({}).states;
        this.queueDraw();
      },
    });
  }

  ngAfterViewChecked(): void {
    this.moveIndicator();
    if (!this.drawQueued) {
      return;
    }
    this.drawQueued = false;
    this.safe('linha', () => this.drawLine());
    this.safe('mapa', () => this.drawMap());
  }

  @HostListener('document:keydown.escape')
  closeOnEscape(): void {
    this.drawer = null;
  }

  selectTab(tab: TabId): void {
    this.tab = tab;
    this.queueDraw();
  }

  onMetric(id: string): void {
    this.metricId = id;
    const years = this.years();
    if (!years.includes(this.year)) {
      this.year = years.at(-1) ?? '';
    }
    this.queueDraw();
    this.refreshKpis();
  }

  setYear(year: string): void {
    this.year = year;
    this.queueDraw();
    this.refreshKpis();
  }

  refreshKpis(): void {
    const token = ++this.kpiToken;
    const slots = this.kpis();
    const reduced =
      typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) {
      this.kpiDisplay = slots.map((slot) => slot.value);
      return;
    }
    const targets = this.metrics.slice(0, 4).map((metric) => ({
      metric,
      value: this.national(metric.id, this.yearOf(metric.id)),
    }));
    const started = performance.now();
    const tick = (now: number) => {
      if (token !== this.kpiToken) {
        return;
      }
      const progress = Math.min(1, (now - started) / 900);
      const eased = 1 - (1 - progress) ** 3;
      this.kpiDisplay = slots.map((slot, index) => {
        const target = targets[index];
        if (!target || target.value === null) {
          return slot.value;
        }
        return formatMetric(target.metric, target.value * eased);
      });
      if (progress < 1) {
        requestAnimationFrame(tick);
      }
    };
    requestAnimationFrame(tick);
  }

  queueDraw(): void {
    this.drawQueued = true;
  }

  metric(): MetricDef | undefined {
    return this.metrics.find((item) => item.id === this.metricId);
  }

  years(): string[] {
    return yearsFor(this.states, this.metricId);
  }

  national(metricId: string, year: string): number | null {
    const values = this.states
      .map((state) => valueAt(state, metricId, year))
      .filter((value): value is number => value !== null);
    return values.length ? values.reduce((sum, value) => sum + value, 0) : null;
  }

  kpis(): { label: string; value: string; sub: string }[] {
    const slots = this.metrics.slice(0, 4).map((metric) => ({
      label: metric.label,
      value: formatMetric(metric, this.national(metric.id, this.yearOf(metric.id))),
      sub: `${metric.sourceLabel || 'Fonte oficial'} · ${this.yearOf(metric.id) || 'sem competência'} · ${metric.unit}`,
    }));
    while (slots.length < 4) {
      slots.push({ label: 'Sem série publicada', value: '—', sub: 'Indicador ausente neste recorte' });
    }
    return slots;
  }

  top10(): { uf: string; nome: string; text: string; width: number }[] {
    const ranked = this.ranked();
    const max = ranked[0]?.value ?? 0;
    return ranked.slice(0, 10).map((row) => ({
      uf: row.state.uf,
      nome: row.state.nome,
      text: formatMetric(this.metric(), row.value),
      width: max > 0 ? (row.value / max) * 100 : 0,
    }));
  }

  insights(): { num: string; label: string; text: string }[] {
    const ranked = this.ranked();
    const metric = this.metric();
    if (!ranked.length || !metric) {
      return [{ num: '—', label: 'recorte', text: 'Não há dado publicado neste indicador.' }];
    }
    const total = ranked.reduce((sum, row) => sum + row.value, 0);
    const leader = ranked[0];
    const last = ranked[ranked.length - 1];
    const share = total > 0 ? (leader.value / total) * 100 : null;
    const gap = last.value > 0 ? leader.value / last.value : null;
    return [
      {
        num: share === null ? '—' : `${share.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`,
        label: 'maior parte',
        text: `${leader.state.nome} concentra a maior parcela publicada de ${metric.label}.`,
      },
      {
        num: gap === null ? '—' : `${gap.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}×`,
        label: 'intervalo',
        text: `Entre ${leader.state.nome} e ${last.state.nome}, na competência ${this.year || '—'}.`,
      },
      {
        num: String(ranked.length),
        label: 'de 27',
        text: 'Unidades da federação com valor publicado. As demais ficam fora da coloração.',
      },
    ];
  }

  series(): { year: string; value: number }[] {
    return this.years()
      .map((year) => ({ year, value: this.national(this.metricId, year) }))
      .filter((point): point is { year: string; value: number } => point.value !== null);
  }

  ranked(): { state: AtlasState; value: number }[] {
    return this.states
      .map((state) => ({ state, value: valueAt(state, this.metricId, this.year) }))
      .filter((row): row is { state: AtlasState; value: number } => row.value !== null)
      .sort((a, b) => b.value - a.value);
  }

  samples(): number[] {
    return this.ranked().map((row) => row.value);
  }

  legend(): { fill: string; text: string }[] {
    const metric = this.metric();
    const samples = this.samples();
    if (!metric || samples.length < 2) {
      return [];
    }
    const sorted = [...samples].sort((a, b) => a - b);
    const at = (portion: number) => sorted[Math.floor(portion * (sorted.length - 1))];
    const cuts = [0.2, 0.4, 0.6, 0.8].map(at);
    return metric.ramp.map((fill, index) => {
      const lo = index === 0 ? null : cuts[index - 1];
      const hi = index === metric.ramp.length - 1 ? null : cuts[index];
      const text =
        lo === null
          ? `até ${formatMetric(metric, hi)}`
          : hi === null
            ? `${formatMetric(metric, lo)} ou mais`
            : `${formatMetric(metric, lo)} – ${formatMetric(metric, hi)}`;
      return { fill, text };
    });
  }

  highlights(): { label: string; text: string }[] {
    const ranked = this.ranked();
    const metric = this.metric();
    if (!ranked.length || !metric) {
      return [
        { label: 'Líder', text: '—' },
        { label: 'Último', text: '—' },
      ];
    }
    const values = ranked.map((row) => row.value).sort((a, b) => a - b);
    const mid = values[Math.floor(values.length / 2)];
    const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
    return [
      { label: 'Líder', text: `${ranked[0].state.uf} · ${formatMetric(metric, ranked[0].value)}` },
      {
        label: 'Último',
        text: `${ranked[ranked.length - 1].state.uf} · ${formatMetric(metric, ranked[ranked.length - 1].value)}`,
      },
      { label: 'Média', text: formatMetric(metric, mean) },
      { label: 'Mediana', text: formatMetric(metric, mid) },
    ];
  }

  tableRows(): AtlasState[] {
    const term = foldYear(this.query.trim());
    const rows = this.states.filter((state) => {
      if (!term) {
        return true;
      }
      return foldYear(state.nome).includes(term) || foldYear(state.uf).includes(term);
    });
    const dir = this.sortDesc ? -1 : 1;
    return [...rows].sort((a, b) => {
      if (this.sortId === 'nome') {
        return a.nome.localeCompare(b.nome, 'pt-BR') * dir;
      }
      if (this.sortId === 'uf') {
        return a.uf.localeCompare(b.uf) * dir;
      }
      const av = valueAt(a, this.sortId, this.year);
      const bv = valueAt(b, this.sortId, this.year);
      if (av === null && bv === null) {
        return 0;
      }
      if (av === null) {
        return 1;
      }
      if (bv === null) {
        return -1;
      }
      return (av - bv) * dir;
    });
  }

  sortBy(id: string): void {
    if (this.sortId === id) {
      this.sortDesc = !this.sortDesc;
    } else {
      this.sortId = id;
      this.sortDesc = id !== 'nome' && id !== 'uf';
    }
  }

  cell(state: AtlasState, metricId: string): string {
    return formatMetric(
      this.metrics.find((item) => item.id === metricId),
      valueAt(state, metricId, this.yearOf(metricId)),
    );
  }

  openUf(uf: string): void {
    const state = this.states.find((item) => item.uf === uf);
    if (state) {
      this.open(state);
    }
  }

  open(state: AtlasState): void {
    this.drawer = state;
    this.queueDraw();
    setTimeout(() => document.getElementById('atlas-drawer-close')?.focus(), 30);
  }

  goRanking(uf: string): void {
    this.tab = 'rankings';
    this.flashUf = uf;
    this.drawer = null;
    this.queueDraw();
    setTimeout(() => {
      document.querySelector(`tr[data-uf="${uf}"]`)?.scrollIntoView({ block: 'center' });
    }, 40);
  }

  addCompared(uf: string): void {
    if (this.compared.includes(uf)) {
      this.tab = 'comparar';
      this.drawer = null;
      return;
    }
    if (this.compared.length >= 3) {
      this.toast = 'O comparador aceita até 3 estados.';
      return;
    }
    this.compared = [...this.compared, uf];
    this.toast = '';
  }

  removeCompared(uf: string): void {
    this.compared = this.compared.filter((item) => item !== uf);
  }

  comparedStates(): AtlasState[] {
    return this.compared
      .map((uf) => this.states.find((state) => state.uf === uf))
      .filter((state): state is AtlasState => !!state);
  }

  best(metricId: string): string | null {
    const rows = this.comparedStates()
      .map((state) => ({ uf: state.uf, value: valueAt(state, metricId, this.yearOf(metricId)) }))
      .filter((row): row is { uf: string; value: number } => row.value !== null);
    if (!rows.length) {
      return null;
    }
    return rows.sort((a, b) => b.value - a.value)[0].uf;
  }

  rankLabel(state: AtlasState, metricId: string): string {
    const value = valueAt(state, metricId, this.yearOf(metricId));
    if (value === null) {
      return '—';
    }
    const ordered = this.states
      .map((item) => valueAt(item, metricId, this.yearOf(metricId)))
      .filter((item): item is number => item !== null)
      .sort((a, b) => b - a);
    return `${ordered.indexOf(value) + 1}º de ${ordered.length}`;
  }

  regionName(state: AtlasState): string {
    return REGION_NAME[state.reg];
  }

  private yearOf(metricId: string): string {
    return metricId === this.metricId ? this.year : (yearsFor(this.states, metricId).at(-1) ?? '');
  }

  private moveIndicator(): void {
    const button = this.tabButtons?.find((item) => item.nativeElement.dataset['tab'] === this.tab);
    if (!button) {
      return;
    }
    const left = button.nativeElement.offsetLeft;
    const width = button.nativeElement.offsetWidth;
    if (left !== this.indicatorLeft) {
      this.indicatorLeft = left;
    }
    if (width !== this.indicatorWidth) {
      this.indicatorWidth = width;
    }
  }

  private drawLine(): void {
    const svg = this.lineChart?.nativeElement;
    if (!svg) {
      return;
    }
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }
    const points = this.series();
    if (points.length < 2) {
      return;
    }
    const width = 780;
    const height = 280;
    const margin = { t: 24, r: 16, b: 32, l: 72 };
    const values = points.map((point) => point.value);
    const lo = Math.min(...values);
    const hi = Math.max(...values);
    const span = hi - lo || 1;
    const x = (index: number) => margin.l + (index * (width - margin.l - margin.r)) / (points.length - 1);
    const y = (value: number) => margin.t + (1 - (value - lo) / span) * (height - margin.t - margin.b);
    const poly = points.map((point, index) => `${x(index)},${y(point.value)}`).join(' ');
    this.svg(svg, 'polyline', { points: poly, fill: 'none', stroke: '#1E4D3B', 'stroke-width': '2.5' });
    const cursor = this.svg(svg, 'line', {
      y1: String(margin.t),
      y2: String(height - margin.b),
      stroke: '#605B4C',
      'stroke-dasharray': '3 3',
    });
    cursor.setAttribute('visibility', 'hidden');
    const tip = this.svg(svg, 'g', {});
    tip.setAttribute('visibility', 'hidden');
    const tipBg = this.svg(tip, 'rect', { fill: '#1A1913', rx: '6', height: '22', y: '-18' });
    const tipText = this.svg(tip, 'text', {
      fill: '#F4F0E5',
      'font-size': '12',
      'font-weight': '600',
      y: '-3',
    });
    points.forEach((point, index) => {
      this.svg(svg, 'circle', { cx: String(x(index)), cy: String(y(point.value)), r: '3.5', fill: '#1E4D3B' });
      const label = this.svg(svg, 'text', {
        x: String(x(index)),
        y: String(height - 8),
        'text-anchor': 'middle',
        fill: '#605B4C',
        'font-size': '12',
      });
      label.textContent = point.year;
    });
    const hit = this.svg(svg, 'rect', {
      x: String(margin.l),
      y: String(margin.t),
      width: String(width - margin.l - margin.r),
      height: String(height - margin.t - margin.b),
      fill: 'transparent',
    });
    hit.addEventListener('mousemove', (event: Event) => {
      const mouse = event as MouseEvent;
      const bounds = svg.getBoundingClientRect();
      const local = ((mouse.clientX - bounds.left) / bounds.width) * width;
      let nearest = 0;
      points.forEach((_, index) => {
        if (Math.abs(x(index) - local) < Math.abs(x(nearest) - local)) {
          nearest = index;
        }
      });
      const point = points[nearest];
      const label = `${point.year}: ${formatMetric(this.metric(), point.value)}`;
      cursor.setAttribute('x1', String(x(nearest)));
      cursor.setAttribute('x2', String(x(nearest)));
      cursor.setAttribute('visibility', 'visible');
      tipText.textContent = label;
      const textWidth = Math.max(72, label.length * 6.4);
      tipBg.setAttribute('width', String(textWidth + 16));
      tipBg.setAttribute('x', String(-8));
      const tipX = Math.min(x(nearest) - textWidth / 2, width - margin.r - textWidth);
      tip.setAttribute('transform', `translate(${Math.max(margin.l, tipX)} ${y(point.value) - 8})`);
      tip.setAttribute('visibility', 'visible');
      this.lineTip = label;
    });
    hit.addEventListener('mouseleave', () => {
      cursor.setAttribute('visibility', 'hidden');
      tip.setAttribute('visibility', 'hidden');
      this.lineTip = '';
    });
  }

  radar(): { uf: string; points: string }[] {
    if (this.metrics.length < 2 || this.comparedStates().length < 2) {
      return [];
    }
    const cx = 110;
    const cy = 110;
    const radius = 78;
    return this.comparedStates().flatMap((state) => {
      const coords = this.metrics.map((metric, index) => {
        const samples = this.states
          .map((item) => valueAt(item, metric.id, this.yearOf(metric.id)))
          .filter((value): value is number => value !== null);
        const value = valueAt(state, metric.id, this.yearOf(metric.id));
        if (value === null || !samples.length) {
          return null;
        }
        const max = Math.max(...samples);
        const ratio = max > 0 ? value / max : 0;
        const angle = -Math.PI / 2 + (index * 2 * Math.PI) / this.metrics.length;
        return `${cx + radius * ratio * Math.cos(angle)},${cy + radius * ratio * Math.sin(angle)}`;
      });
      if (coords.some((coord) => coord === null)) {
        return [];
      }
      return [{ uf: state.uf, points: coords.join(' ') }];
    });
  }

  private drawMap(): void {
    const svg = this.hexmap?.nativeElement;
    if (!svg) {
      return;
    }
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }
    const metric = this.metric();
    const samples = this.samples();
    for (const label of REGION_LABELS) {
      const node = this.svg(svg, 'text', {
        class: 'map-region-label',
        x: String(label.x),
        y: String(label.y),
      });
      node.textContent = label.t;
    }
    const sx = Math.sqrt(3) * HR;
    const sy = 1.5 * HR;
    for (const state of this.states) {
      const cx = (state.col + (state.row % 2 ? 0.5 : 0)) * sx;
      const cy = state.row * sy;
      const value = valueAt(state, this.metricId, this.year);
      const fill = metric ? quantileFill(value, samples, metric.ramp) : null;
      const paint = fill ?? '#E1DBC8';
      const group = this.svg(svg, 'g', {
        class: this.drawer?.uf === state.uf ? 'hexg selected' : 'hexg',
        tabindex: '0',
        role: 'button',
      });
      group.setAttribute(
        'aria-label',
        `${state.nome}. ${metric?.label ?? 'Indicador'} ${formatMetric(metric, value)}.`,
      );
      this.svg(group, 'path', { d: this.hexPath(cx, cy), fill: paint });
      const text = this.svg(group, 'text', {
        class: 'hex-label',
        x: String(cx),
        y: String(cy + 1),
        fill: textOn(paint),
      });
      text.textContent = state.uf;
      group.addEventListener('click', () => this.open(state));
      group.addEventListener('keydown', (event: Event) => {
        const key = (event as KeyboardEvent).key;
        if (key === 'Enter' || key === ' ') {
          event.preventDefault();
          this.open(state);
        }
      });
      group.addEventListener('mouseenter', (event: Event) => this.placeTip(state, event as MouseEvent));
      group.addEventListener('mouseleave', () => this.hideTip());
    }
  }

  tip = { on: false, left: 0, top: 0, uf: '', nome: '', region: '', value: '' };

  private placeTip(state: AtlasState, event: MouseEvent): void {
    this.tip = {
      on: true,
      left: Math.min(event.clientX + 16, window.innerWidth - 250),
      top: Math.max(10, event.clientY - 80),
      uf: state.uf,
      nome: state.nome,
      region: REGION_NAME[state.reg],
      value: formatMetric(this.metric(), valueAt(state, this.metricId, this.year)),
    };
  }

  private hideTip(): void {
    this.tip = { ...this.tip, on: false };
  }

  regionColor(state: AtlasState): string {
    return REGION_COLOR[state.reg];
  }

  private hexPath(cx: number, cy: number): string {
    const points: string[] = [];
    for (let step = 0; step < 6; step += 1) {
      const angle = ((-90 + 60 * step) * Math.PI) / 180;
      points.push(`${(cx + HR * Math.cos(angle)).toFixed(1)},${(cy + HR * Math.sin(angle)).toFixed(1)}`);
    }
    return `M${points.join('L')}Z`;
  }

  private svg(parent: SVGElement, name: string, attrs: Record<string, string>): SVGElement {
    const node = document.createElementNS(SVGNS, name);
    for (const [key, value] of Object.entries(attrs)) {
      node.setAttribute(key, value);
    }
    parent.appendChild(node);
    return node;
  }

  private safe(label: string, fn: () => void): void {
    try {
      fn();
    } catch (error) {
      console.error(`[Atlas] Falha ao renderizar ${label}:`, error);
    }
  }
}
