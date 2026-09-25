import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import type { EChartsOption } from 'echarts';
import * as echarts from 'echarts';
import { NgxEchartsDirective, provideEcharts } from 'ngx-echarts';
import { catchError, forkJoin, of } from 'rxjs';
import {
  formatPublishedValue,
  humanizeUnit,
} from '../shared/presentation/official-labels';
import { ErrorStateComponent } from '../shared/states/error-state.component';
import { SkeletonComponent } from '../shared/states/skeleton.component';

interface GeographyMeasure {
  sourceId: string;
  sourceLabel: string;
  label: string;
  unit: string;
  competence: string;
  total: number;
  municipalityCount: number;
}

interface GeographyState {
  uf: string;
  name: string;
  regionId: string;
  measures: GeographyMeasure[];
}

interface GeographyRegion {
  id: string;
  name: string;
  states: GeographyState[];
}

interface GeographyResponse {
  createsTaxCredit: boolean;
  regions: GeographyRegion[];
}

interface RegionMesh {
  type: 'FeatureCollection';
  features: { properties?: { name?: string } }[];
}

type MapState = 'loading' | 'ok' | 'error';

@Component({
  selector: 'app-brazil-region-map',
  standalone: true,
  imports: [CommonModule, FormsModule, NgxEchartsDirective, ErrorStateComponent, SkeletonComponent],
  providers: [provideEcharts()],
  template: `
    <section class="region-map" aria-labelledby="region-map-title">
      <header class="region-head">
        <div>
          <h2 id="region-map-title">Mapa do Brasil</h2>
          <p>Uma medida por vez, somada a partir das séries oficiais já publicadas.</p>
        </div>
        <form class="filters" aria-label="Filtros do mapa">
          <label>
            Região
            <select [(ngModel)]="regionFilter" name="region" (ngModelChange)="applyFilters()">
              <option value="">Todas</option>
              @for (region of regions; track region.id) {
                <option [value]="region.id">{{ region.name }}</option>
              }
            </select>
          </label>
          <label>
            Indicador
            <select [(ngModel)]="indicatorFilter" name="indicator" (ngModelChange)="applyFilters()">
              @for (option of indicatorOptions; track option.id) {
                <option [value]="option.id">{{ option.label }}</option>
              }
            </select>
          </label>
          <label>
            Ano
            <select [(ngModel)]="yearFilter" name="year" (ngModelChange)="applyFilters()">
              @for (year of yearOptions; track year) {
                <option [value]="year">{{ year }}</option>
              }
            </select>
          </label>
        </form>
      </header>

      @if (state === 'loading') {
        <app-skeleton />
      }
      @if (state === 'error') {
        <app-error-state
          title="Mapa indisponível"
          message="Não foi possível ler as séries publicadas por região. O restante do painel continua disponível."
        />
      }
      @if (state === 'ok') {
        <div class="stage">
          <div
            echarts
            class="canvas"
            [options]="options"
            (chartClick)="onChartClick($event)"
            role="img"
            [attr.aria-label]="mapLabel"
          ></div>
          <div class="side">
            @if (selected) {
              <article class="detail" aria-labelledby="region-detail-title">
                <header>
                  <h3 id="region-detail-title">{{ selected.name }}</h3>
                  <button type="button" (click)="closeDetail()">Fechar</button>
                </header>
                <p>{{ summary(selected) }}</p>
                <ul>
                  @for (item of stateRows(selected); track item.uf) {
                    <li>
                      <strong>{{ item.name }}</strong>
                      <span>{{ item.text }}</span>
                    </li>
                  }
                </ul>
              </article>
            } @else {
              <p id="region-focus" class="focus" aria-live="polite">{{ focusText }}</p>
            }
            <ul class="region-list" aria-label="Regiões do mapa">
              @for (region of visibleRegions; track region.id) {
                <li>
                  <button
                    type="button"
                    (click)="openRegion(region)"
                    (focus)="focusRegion(region)"
                    [attr.aria-describedby]="'region-focus'"
                  >
                    {{ region.name }}
                  </button>
                </li>
              }
            </ul>
            <p class="credit">Malha territorial das regiões: IBGE.</p>
          </div>
        </div>
      }
    </section>
  `,
  styles: `
    .region-map {
      display: grid;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }
    .region-head,
    .filters,
    .stage,
    .detail header {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      align-items: end;
      justify-content: space-between;
    }
    .filters label {
      display: grid;
      gap: 0.25rem;
      font-size: 0.875rem;
    }
    .stage {
      align-items: stretch;
    }
    .canvas {
      flex: 1 1 28rem;
      height: 28rem;
      min-width: 16rem;
    }
    .side {
      flex: 1 1 16rem;
      display: grid;
      align-content: start;
      gap: 0.75rem;
    }
    .region-list {
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 0.5rem;
    }
    .region-list button,
    .detail button,
    .filters select {
      font: inherit;
    }
    .detail ul {
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 0.5rem;
    }
    .detail li {
      display: flex;
      justify-content: space-between;
      gap: 1rem;
    }
    .credit,
    .focus {
      color: var(--ink-700, #334155);
      font-size: 0.875rem;
    }
  `,
})
export class BrazilRegionMapComponent implements OnInit {
  private readonly http = inject(HttpClient);

  state: MapState = 'loading';
  regions: GeographyRegion[] = [];
  visibleRegions: GeographyRegion[] = [];
  indicatorOptions: { id: string; label: string }[] = [];
  yearOptions: string[] = [];
  regionFilter = '';
  indicatorFilter = '';
  yearFilter = '';
  selected: GeographyRegion | null = null;
  focusText = 'Passe o foco por uma região para ler o total publicado.';
  mapLabel = 'Mapa das cinco regiões do Brasil';
  options: EChartsOption = {};
  private mesh: RegionMesh | null = null;

  ngOnInit(): void {
    forkJoin({
      mesh: this.http.get<RegionMesh>('/geo/br-regioes.json'),
      geography: this.http
        .get<GeographyResponse>('/v1/dashboards/executivo/geography')
        .pipe(catchError((error: HttpErrorResponse) => of(error))),
    }).subscribe(({ mesh, geography }) => {
      if (geography instanceof HttpErrorResponse || !mesh?.features?.length) {
        this.state = 'error';
        return;
      }
      this.mesh = mesh;
      this.regions = geography.regions ?? [];
      this.indicatorOptions = this.collectIndicators();
      this.yearOptions = this.collectYears();
      this.indicatorFilter = this.indicatorOptions[0]?.id ?? '';
      this.yearFilter = this.yearOptions[0] ?? '';
      this.applyFilters();
      this.state = 'ok';
    });
  }

  applyFilters(): void {
    this.visibleRegions = this.regionFilter
      ? this.regions.filter((region) => region.id === this.regionFilter)
      : [...this.regions];
    if (this.selected && !this.visibleRegions.some((region) => region.id === this.selected?.id)) {
      this.selected = null;
    }
    this.publishMap();
  }

  openRegion(region: GeographyRegion): void {
    this.selected = region;
    this.focusRegion(region);
  }

  closeDetail(): void {
    this.selected = null;
  }

  focusRegion(region: GeographyRegion): void {
    this.focusText = this.summary(region);
  }

  onChartClick(event: { name?: string }): void {
    const region = this.visibleRegions.find((item) => item.name === event.name);
    if (region) {
      this.openRegion(region);
    }
  }

  summary(region: GeographyRegion): string {
    const measure = this.regionMeasure(region);
    if (!measure) {
      return `${region.name}. Não há dado publicado neste recorte.`;
    }
    return (
      `${region.name}. ${measure.label}: ${formatPublishedValue(measure.total, measure.unit)} ` +
      `${humanizeUnit(measure.unit)}. Competência ${measure.competence}. ${measure.sourceLabel}. ` +
      `${measure.municipalityCount} municípios.`
    );
  }

  stateRows(region: GeographyRegion): { uf: string; name: string; text: string }[] {
    return region.states.map((state) => {
      const measure = this.pick(state.measures);
      return {
        uf: state.uf,
        name: state.name,
        text: measure
          ? `${formatPublishedValue(measure.total, measure.unit)} ${humanizeUnit(measure.unit)} · ${measure.competence}`
          : 'Não há dado publicado neste recorte.',
      };
    });
  }

  mapValues(): (number | null)[] {
    return this.visibleRegions.map((region) => this.regionMeasure(region)?.total ?? null);
  }

  private publishMap(): void {
    if (!this.mesh) {
      return;
    }
    const names = new Set(this.visibleRegions.map((region) => region.name));
    const mesh = {
      ...this.mesh,
      features: this.mesh.features.filter((feature) => names.has(feature.properties?.name ?? '')),
    };
    echarts.registerMap('brasil-regioes', mesh as never);
    const data = this.visibleRegions.map((region) => {
      const measure = this.regionMeasure(region);
      return {
        name: region.name,
        value: measure?.total,
        summary: this.summary(region),
      };
    });
    this.mapLabel = data.map((item) => item.summary).join(' ');
    this.options = {
      tooltip: {
        trigger: 'item',
        formatter: (params: unknown) => {
          const row = params as { data?: { summary?: string } };
          return row.data?.summary ?? '';
        },
      },
      series: [
        {
          type: 'map',
          map: 'brasil-regioes',
          nameProperty: 'name',
          data,
          selectedMode: 'single',
        },
      ],
    };
  }

  private regionMeasure(region: GeographyRegion): GeographyMeasure | null {
    const matches = region.states.flatMap((state) => this.pick(state.measures) ?? []);
    if (!matches.length) {
      return null;
    }
    const first = matches[0];
    return {
      ...first,
      total: matches.reduce((sum, item) => sum + item.total, 0),
      municipalityCount: matches.reduce((sum, item) => sum + item.municipalityCount, 0),
    };
  }

  private pick(measures: GeographyMeasure[]): GeographyMeasure | null {
    return (
      measures.find(
        (measure) =>
          this.indicatorId(measure) === this.indicatorFilter &&
          measure.competence === this.yearFilter,
      ) ?? null
    );
  }

  private collectIndicators(): { id: string; label: string }[] {
    const seen = new Map<string, string>();
    for (const region of this.regions) {
      for (const state of region.states) {
        for (const measure of state.measures) {
          seen.set(this.indicatorId(measure), measure.label);
        }
      }
    }
    return [...seen.entries()].map(([id, label]) => ({ id, label }));
  }

  private collectYears(): string[] {
    const years = new Set<string>();
    for (const region of this.regions) {
      for (const state of region.states) {
        for (const measure of state.measures) {
          if (measure.competence) {
            years.add(measure.competence);
          }
        }
      }
    }
    return [...years].sort((left, right) => right.localeCompare(left));
  }

  private indicatorId(measure: GeographyMeasure): string {
    return `${measure.sourceId}::${measure.label}`;
  }
}
