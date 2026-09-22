import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app.component';
import { APP_NAV_GROUPS } from './layout/navigation';

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [provideRouter([]), provideHttpClient()],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('renders grouped navigation without the version in the header', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const sidebar = compiled.querySelector('aside[aria-label="Navegação principal"]');
    expect(sidebar?.textContent).toContain('SIRTA');
    expect(sidebar?.textContent).toContain('Visão executiva');
    expect(sidebar?.textContent).toContain('Cobrança');
    expect(compiled.querySelector('header')?.textContent).not.toContain('0.3.');
    expect(compiled.querySelectorAll('aside nav, aside a[routerlink], aside a').length).toBeGreaterThan(0);
    const labels = APP_NAV_GROUPS.flatMap((group) => group.links).length;
    expect(compiled.querySelectorAll('aside a[href], aside a').length).toBeGreaterThanOrEqual(labels);
  });
});
