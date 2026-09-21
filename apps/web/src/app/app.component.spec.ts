import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app.component';
import { APP_IMPLEMENTATION_VERSION } from './app.shell';

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

  it('should render brand, version and grouped navigation', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const header = compiled.querySelector('header');
    expect(header?.textContent).toContain('SIRTA Municipal');
    expect(header?.textContent).toContain(APP_IMPLEMENTATION_VERSION);
    expect(compiled.querySelectorAll('.shell-nav-group').length).toBeGreaterThan(3);
    expect(compiled.querySelector('nav[aria-label="Principal"]')).toBeTruthy();
  });
});
