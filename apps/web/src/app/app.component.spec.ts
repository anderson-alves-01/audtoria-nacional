import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app.component';
import { APP_DASHBOARD_NAV, APP_IMPLEMENTATION_VERSION } from './app.shell';

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [provideRouter([])],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should render brand, version and official dashboard navigation', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const header = compiled.querySelector('header');
    expect(header?.textContent).toContain('SIRTA Municipal');
    expect(header?.textContent).toContain(APP_IMPLEMENTATION_VERSION);
    expect(compiled.querySelector('nav[aria-label="Painéis oficiais"]')).toBeTruthy();
    expect(compiled.querySelectorAll('.shell-nav-primary .shell-nav-list a').length).toBe(
      APP_DASHBOARD_NAV.length,
    );
    expect(header?.textContent).toContain('Executivo');
    expect(header?.textContent).toContain('Cobrança');
  });
});
