import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router, Routes } from '@angular/router';
import { routes } from './app.routes';

describe('routes', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideRouter(routes), provideHttpClient()],
    });
  });

  it('opens the login screen before the Tax Better vision', async () => {
    sessionStorage.clear();
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/');
    expect(router.url).toBe('/entrar');
  });

  it('opens the Tax Better vision after login', async () => {
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
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/');
    expect(router.url).toBe('/visao');
  });

  it('sends an unauthenticated visitor of the Simulador to the login screen', async () => {
    sessionStorage.clear();
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/simulador');
    expect(router.url).toBe('/entrar');
  });

  it('opens the Simulador for a signed-in operator', async () => {
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
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/simulador');
    expect(router.url).toBe('/simulador');
    sessionStorage.clear();
  });

  it('keeps the Simulador only inside the guarded shell', () => {
    const shell = routes.find((route) => route.path === '' && route.component !== undefined);
    expect(shell?.canActivate?.length).toBeGreaterThan(0);
    expect((shell?.children ?? []).some((child) => child.path === 'simulador')).toBeTrue();
    expect(routes.some((route) => route.path === 'simulador')).toBeFalse();
  });
  it('keeps legacy dashboard and sectoral urls', () => {
    const paths = collect(routes);
    expect(paths).toContain('setorial');
    expect(paths).toContain('financeiro');
    expect(paths).toContain('saude');
    expect(paths).toContain('procuradoria');
    expect(paths).toContain('integracao');
    expect(paths).toContain('administracao');
    expect(paths).toContain('entrar');
  });
});

function collect(items: Routes): string[] {
  return items.flatMap((route) => [route.path ?? '', ...collect(route.children ?? [])]);
}
