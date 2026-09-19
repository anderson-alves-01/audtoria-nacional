import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { Cadastro360PageComponent } from './cadastro-360-page.component';

describe('Cadastro360PageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Cadastro360PageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty Cadastro 360 without PII or invented territory', () => {
    const fixture = TestBed.createComponent(Cadastro360PageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/cadastro-360').flush({
      version: 'cadastro-360-technical-v1',
      piiPresent: false,
      territoryInvented: false,
      g0Status: 'BLOCKED',
      minimizationPolicy: [
        { field: 'cpf_cnpj', policy: 'MASKED_OR_ABSENT', present: false },
      ],
      subjects: [],
      disclaimer: 'Cadastro 360 técnico vazio.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Cadastro 360');
    expect(text).toContain('PII presente: não');
    expect(text).toContain('Território inventado: não');
    expect(text).toContain('cpf_cnpj');
    expect(text).toContain('BLOCKED');
    http.verify();
  });

  it('shows error when Cadastro 360 API fails', () => {
    const fixture = TestBed.createComponent(Cadastro360PageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/cadastro-360').flush(
      { title: 'Error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar o Cadastro 360',
    );
    http.verify();
  });
});
