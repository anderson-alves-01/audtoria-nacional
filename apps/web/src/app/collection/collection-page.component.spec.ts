import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { CollectionPageComponent } from './collection-page.component';

describe('CollectionPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CollectionPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('keeps an idle instruction before submit', () => {
    const fixture = TestBed.createComponent(CollectionPageComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('VALIDATED e ENFORCEABLE');
  });

  it('shows a blocked-credit message on conflict', () => {
    const fixture = TestBed.createComponent(CollectionPageComponent);
    const page = fixture.componentInstance;
    const http = TestBed.inject(HttpTestingController);
    page.creditId = '11111111-1111-4111-8111-111111111051';
    page.submit();
    http.expectOne('/v1/tax-credits/11111111-1111-4111-8111-111111111051/collection-cases').flush(
      { title: 'Conflict' },
      { status: 409, statusText: 'Conflict' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('O crédito não foi alterado');
    http.verify();
  });
});
