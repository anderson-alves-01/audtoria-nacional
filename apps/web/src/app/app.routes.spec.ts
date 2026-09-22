import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { routes } from './app.routes';

describe('routes', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideRouter(routes), provideHttpClient()],
    });
  });

  it('opens the executive view from the root path', async () => {
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/');
    expect(router.url).toBe('/executivo');
  });

  it('keeps legacy dashboard and sectoral urls', () => {
    const paths = routes.map((route) => route.path);
    expect(paths).toContain('setorial');
    expect(paths).toContain('financeiro');
    expect(paths).toContain('saude');
    expect(paths).toContain('procuradoria');
  });
});
