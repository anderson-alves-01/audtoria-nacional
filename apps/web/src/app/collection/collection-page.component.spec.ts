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

  it('renders empty official collection panel with commands disabled', () => {
    const fixture = TestBed.createComponent(CollectionPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/collection').flush({
      version: 'collection-panel-technical-v1',
      commandsDisabled: true,
      sendEnabled: false,
      createsTaxCredit: false,
      g0Status: 'BLOCKED',
      g4Status: 'BLOCKED',
      g5Status: 'BLOCKED',
      items: [],
      queue: [],
      disclaimer: 'Painel de cobrança administrativa oficial vazio.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Cobrança administrativa (painel oficial)');
    expect(text).toContain('G0: BLOCKED');
    expect(text).toContain('G5: BLOCKED');
    expect(text).toContain('Comandos desativados');
    expect(text).toContain('Sem cobrança iniciada');
    http.verify();
  });

  it('shows error when collection panel API fails', () => {
    const fixture = TestBed.createComponent(CollectionPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/collection').flush(
      { title: 'Error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar o painel de cobrança',
    );
    http.verify();
  });
});
