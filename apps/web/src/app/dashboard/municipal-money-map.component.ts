import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { AfterViewChecked, Component, ElementRef, HostListener, OnInit, ViewChild, inject } from '@angular/core';
import {
  AtlasState,
  GeographyPayload,
  MetricDef,
  adaptMoneyGeography,
  formatPublishedReais,
  quantileFill,
  textOn,
  valueAt,
  yearsFor,
} from '../atlas/geography-adapter';
import { REGION_LABELS, REGION_NAME } from '../atlas/hex-layout';

const SVGNS = 'http://www.w3.org/2000/svg';
const HR = 34;

@Component({
  selector: 'app-municipal-money-map',
  standalone: true,
  templateUrl: './municipal-money-map.component.html',
  styleUrl: './municipal-money-map.component.scss',
})
export class MunicipalMoneyMapComponent implements OnInit, AfterViewChecked {
  private readonly http = inject(HttpClient);

  @ViewChild('hexmap') hexmap?: ElementRef<SVGSVGElement>;

  loading = true;
  failed = false;
  states: AtlasState[] = [];
  metrics: MetricDef[] = [];
  metricId = '';
  year = '';
  drawer: AtlasState | null = null;
  tip = { on: false, left: 0, top: 0, nome: '', value: '' };
  private drawQueued = false;

  ngOnInit(): void {
    this.http.get<GeographyPayload>('/v1/dashboards/financeiro/geography').subscribe({
      next: (payload) => {
        this.apply(adaptMoneyGeography(payload));
        this.loading = false;
        this.queueDraw();
      },
      error: (_error: HttpErrorResponse) => {
        this.apply(adaptMoneyGeography({}));
        this.failed = true;
        this.loading = false;
        this.queueDraw();
      },
    });
  }

  ngAfterViewChecked(): void {
    if (!this.drawQueued) {
      return;
    }
    this.drawQueued = false;
    this.drawMap();
  }

  @HostListener('document:keydown.escape')
  close(): void {
    this.drawer = null;
    this.queueDraw();
  }

  years(): string[] {
    return yearsFor(this.states, this.metricId);
  }

  metric(): MetricDef | undefined {
    return this.metrics.find((item) => item.id === this.metricId);
  }

  selectMetric(id: string): void {
    this.metricId = id;
    const years = this.years();
    if (!years.includes(this.year)) {
      this.year = years.at(-1) ?? '';
    }
    this.queueDraw();
  }

  selectYear(year: string): void {
    this.year = year;
    this.queueDraw();
  }

  selectValue(event: Event): string {
    return (event.target as HTMLSelectElement).value;
  }

  detailText(): string {
    if (!this.drawer) {
      return '';
    }
    const point = this.point(this.drawer);
    const value = formatPublishedReais(point?.value ?? null);
    if (!point || point.value === null) {
      return `${this.drawer.nome} não tem valor publicado nesta série.`;
    }
    const count = point.municipalityCount ?? 0;
    const places = count === 1 ? '1 município na soma' : `${count} municípios na soma`;
    return `${value}. ${places}. ${point.sourceLabel}. Competência ${point.year}.`;
  }

  private apply(view: { states: AtlasState[]; metrics: MetricDef[] }): void {
    this.states = view.states;
    this.metrics = view.metrics;
    this.metricId = this.metrics[0]?.id ?? '';
    this.year = this.years().at(-1) ?? '';
  }

  private queueDraw(): void {
    this.drawQueued = true;
  }

  private point(state: AtlasState) {
    return state.points.find((item) => item.metricId === this.metricId && item.year === this.year);
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
    const samples = this.states
      .map((state) => valueAt(state, this.metricId, this.year))
      .filter((value): value is number => value !== null);
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
        `${state.nome}, ${REGION_NAME[state.reg]}. ${metric?.label ?? 'Série'} ${formatPublishedReais(value)}.`,
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
      group.addEventListener('mouseleave', () => {
        this.tip = { ...this.tip, on: false };
      });
    }
  }

  private open(state: AtlasState): void {
    this.drawer = state;
    this.queueDraw();
  }

  private placeTip(state: AtlasState, event: MouseEvent): void {
    this.tip = {
      on: true,
      left: Math.min(event.clientX + 16, window.innerWidth - 240),
      top: Math.max(10, event.clientY - 72),
      nome: state.nome,
      value: formatPublishedReais(valueAt(state, this.metricId, this.year)),
    };
  }

  private hexPath(cx: number, cy: number): string {
    const points: string[] = [];
    for (let step = 0; step < 6; step += 1) {
      const angle = ((-90 + 60 * step) * Math.PI) / 180;
      points.push(
        `${(cx + HR * Math.cos(angle)).toFixed(1)},${(cy + HR * Math.sin(angle)).toFixed(1)}`,
      );
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
}
