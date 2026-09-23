import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { FunnelPageComponent } from './funnel-page.component';

describe('FunnelPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FunnelPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('shows published credit counts without turning them into money', () => {
    const fixture = TestBed.createComponent(FunnelPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/indicators/credit-funnel').flush({
      identifiedCount: 4,
      validatedCount: 2,
      inCollectionCount: 1,
      silverRowCount: 9,
      methodologyVersion: 'credit-funnel-v1',
      published: true,
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Funil de recuperação');
    expect(text).toContain('Identificado');
    expect(text).toContain('Validado');
    expect(text).toContain('Em cobrança');
    expect(text).toContain('Linhas de apoio na carga');
    expect(text).toContain('4');
    expect(text).toContain('Não é valor em reais');
    expect(text).not.toContain('credit-funnel-v1');
    expect(text).not.toContain('R$');
    http.verify();
  });

  it('stays empty when no credit funnel is published', () => {
    const fixture = TestBed.createComponent(FunnelPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/indicators/credit-funnel').flush({
      identifiedCount: 0,
      validatedCount: 0,
      inCollectionCount: 0,
      silverRowCount: 0,
      methodologyVersion: 'credit-funnel-v1',
      published: false,
      note: 'No published synthetic Gold funnel. Regional R$ hypotheses are not KPIs.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Funil sem crédito publicado');
    expect(text).toContain('Dinheiro do Município');
    expect(text).toContain('não é valor a recuperar');
    expect(text).not.toContain('Identificado');
    expect(text).not.toContain('No published synthetic');
    expect(text).not.toContain('R$');
    http.verify();
  });
});
