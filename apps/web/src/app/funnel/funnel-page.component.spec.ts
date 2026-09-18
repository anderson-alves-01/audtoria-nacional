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

  it('renders published funnel counts without regional money', () => {
    const fixture = TestBed.createComponent(FunnelPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/indicators/credit-funnel').flush({
      identifiedCount: 1,
      validatedCount: 0,
      inCollectionCount: 0,
      methodologyVersion: 'credit-funnel-v1',
      published: true,
      note: 'Counts of synthetic tax credits.',
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Identificados: 1');
    expect(fixture.nativeElement.textContent).not.toContain('R$');
    http.verify();
  });
});
