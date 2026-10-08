import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { AppComponent } from './app.component';
import { routes } from './app.routes';
import { APP_NAV_GROUPS } from './layout/navigation';

describe('AppComponent', () => {
  beforeEach(async () => {
    sessionStorage.clear();
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [provideRouter(routes), provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('shows the login screen before any module', async () => {
    const fixture = TestBed.createComponent(AppComponent);
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/visao');
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(router.url).toBe('/entrar');
    expect(text).toContain('Entrar');
    expect(text).not.toContain('Integração');
  });

  it('renders grouped navigation after a successful login', async () => {
    sessionStorage.setItem(
      'sirta.operatorSession',
      JSON.stringify({
        accessToken: 'token',
        territoryId: 'territory',
        purposeId: 'purpose',
        expiresAt: '2099-01-01T00:00:00Z',
        mode: 'OPERATOR_LOGIN',
        username: 'admin.alpha',
      }),
    );
    const fixture = TestBed.createComponent(AppComponent);
    const router = TestBed.inject(Router);
    const http = TestBed.inject(HttpTestingController);
    await router.navigateByUrl('/visao');
    fixture.detectChanges();
    http.expectOne('/v1/tax-better/vision').flush({
      createsTaxCredit: false,
      approvedExport: false,
      emptyReason: 'Ainda não há arquivo autorizado na visão.',
      rows: [],
    });
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const sidebar = compiled.querySelector('aside[aria-label="Navegação principal"]');
    expect(sidebar?.textContent).toContain('SIRTA');
    expect(sidebar?.textContent).toContain('Tax Better');
    expect(sidebar?.textContent).toContain('Integração');
    expect(sidebar?.textContent).toContain('Visão');
    expect(sidebar?.textContent).toContain('Administração');
    expect(sidebar?.textContent).toContain('Referência publicada');
    expect(sidebar?.textContent).not.toContain('Cobrança');
    expect(compiled.querySelector('header')?.textContent).not.toContain('Alertas');
    expect(compiled.querySelector('header')?.textContent).not.toContain('0.3.');
    const openLabels = APP_NAV_GROUPS.filter((group) => group.id !== 'reference').flatMap(
      (group) => group.links,
    ).length;
    expect(compiled.querySelectorAll('aside a[href], aside a').length).toBeGreaterThanOrEqual(openLabels);
    http.verify();
  });
});
