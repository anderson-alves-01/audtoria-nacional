import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { DashboardPageComponent } from './dashboard-page.component';

describe('DashboardPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: ActivatedRoute, useValue: { snapshot: { data: { dashboardId: 'transferencias' } } } },
      ],
    }).compileComponents();
  });

  it('shows empty official state without synthetic values', () => {
    const fixture = TestBed.createComponent(DashboardPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/dashboards/transferencias').flush({
      title: 'Transferências',
      banner: 'DADOS DE FONTE OFICIAL — PROCESSAMENTO TÉCNICO CONCLUÍDO — HOMOLOGAÇÃO HUMANA PENDENTE',
      emptyReason: 'Somente valores oficiais publicados. Dicionário FPM não é valor transferido.',
      published: false,
      commandsDisabled: true,
      items: [],
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Dicionário FPM não é valor transferido');
    expect(fixture.nativeElement.textContent).toContain('Comandos de cobrança');
    expect(fixture.nativeElement.textContent).not.toContain('R$');
    http.verify();
  });
});
