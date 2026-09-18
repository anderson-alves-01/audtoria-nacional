import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { HealthPageComponent } from './health-page.component';

describe('HealthPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HealthPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('shows loading then success state', () => {
    const fixture = TestBed.createComponent(HealthPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Carregando');
    http.expectOne('/health').flush({
      status: 'ok',
      specVersion: '0.3.0',
      implementationVersion: '0.3.3',
      releaseStage: 'S3_COLLECTION',
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Spec 0.3.0');
    http.verify();
  });

  it('shows error state when the API is unavailable', () => {
    const fixture = TestBed.createComponent(HealthPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/health').error(new ProgressEvent('error'));
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Não foi possível obter a saúde da API local.');
    http.verify();
  });
});
