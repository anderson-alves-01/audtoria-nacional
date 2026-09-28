import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MunicipalMoneyMapComponent } from './municipal-money-map.component';

describe('MunicipalMoneyMapComponent', () => {
  let fixture: ComponentFixture<MunicipalMoneyMapComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [MunicipalMoneyMapComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    fixture = TestBed.createComponent(MunicipalMoneyMapComponent);
    fixture.detectChanges();
    TestBed.inject(HttpTestingController).expectOne('/v1/dashboards/financeiro/geography').flush({
      regions: [
        {
          states: [
            {
              uf: 'AC',
              measures: [
                {
                  sourceId: 'TESOURO-FPM-VALORES',
                  sourceLabel: 'FPM publicado',
                  label: 'FPM publicado',
                  unit: 'BRL',
                  competence: '2025',
                  total: 2_500_000,
                  municipalityCount: 22,
                },
              ],
            },
          ],
        },
      ],
    });
    fixture.detectChanges();
  });

  it('shows the published municipal sum on the state', () => {
    const acre = fixture.nativeElement.querySelector('[aria-label^="Acre"]') as SVGGElement;
    expect(acre.getAttribute('aria-label')).toContain('2,5 mi');
    acre.dispatchEvent(new Event('click'));
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('22 municípios na soma');
    expect(fixture.nativeElement.textContent).toContain('não é crédito tributário');
  });
});
