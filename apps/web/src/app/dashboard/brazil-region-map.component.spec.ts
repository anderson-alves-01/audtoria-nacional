import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { BrazilRegionMapComponent } from './brazil-region-map.component';

const mesh = {
  type: 'FeatureCollection',
  features: [
    { properties: { name: 'Norte' }, geometry: { type: 'Polygon', coordinates: [] } },
    { properties: { name: 'Sul' }, geometry: { type: 'Polygon', coordinates: [] } },
  ],
};

const geography = {
  createsTaxCredit: false,
  regions: [
    {
      id: 'norte',
      name: 'Norte',
      states: [
        {
          uf: 'AC',
          name: 'Acre',
          regionId: 'norte',
          measures: [
            {
              sourceId: 'IBGE-SIDRA',
              sourceLabel: 'IBGE — população',
              label: 'População',
              unit: 'Pessoas',
              competence: '2024',
              total: 22,
              municipalityCount: 1,
            },
          ],
        },
      ],
    },
    {
      id: 'sul',
      name: 'Sul',
      states: [
        {
          uf: 'RS',
          name: 'Rio Grande do Sul',
          regionId: 'sul',
          measures: [],
        },
      ],
    },
  ],
};

describe('BrazilRegionMapComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BrazilRegionMapComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  function load(): BrazilRegionMapComponent {
    const fixture = TestBed.createComponent(BrazilRegionMapComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/geo/br-regioes.json').flush(mesh);
    http.expectOne('/v1/dashboards/executivo/geography').flush(geography);
    fixture.detectChanges();
    return fixture.componentInstance;
  }

  it('hides the other regions when one region is filtered', () => {
    const map = load();
    map.regionFilter = 'norte';
    map.applyFilters();
    expect(map.visibleRegions.map((region) => region.id)).toEqual(['norte']);
  });

  it('opens the states of the clicked region', () => {
    const map = load();
    map.onChartClick({ name: 'Norte' });
    expect(map.selected?.name).toBe('Norte');
    expect(map.stateRows(map.selected!).map((row) => row.name)).toEqual(['Acre']);
  });

  it('does not draw a value when the cut has no published line', () => {
    const map = load();
    map.regionFilter = 'sul';
    map.applyFilters();
    expect(map.mapValues()).toEqual([null]);
    expect(map.summary(map.visibleRegions[0])).toContain('Não há dado publicado neste recorte');
    expect(map.summary(map.visibleRegions[0])).not.toMatch(/\d/);
  });
});
