import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ProcuradoriaPageComponent } from './procuradoria-page.component';

describe('ProcuradoriaPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProcuradoriaPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty official Procuradoria workflow with legal commands disabled', () => {
    const fixture = TestBed.createComponent(ProcuradoriaPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/procuradoria').flush({
      version: 'procuradoria-panel-technical-v1',
      commandsDisabled: true,
      legalCommandsEnabled: false,
      altersLegalStatus: false,
      createsTaxCredit: false,
      g6Status: 'LOCAL_GO_OFFICIAL_BLOCKED',
      items: [],
      queue: [],
      disclaimer: 'Workflow técnico da Procuradoria vazio.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Procuradoria (workflow oficial)');
    expect(text).toContain('LOCAL_GO_OFFICIAL_BLOCKED');
    expect(text).toContain('Comandos jurídicos desativados');
    expect(text).toContain('Sem encaminhamento automático');
    http.verify();
  });

  it('shows error when Procuradoria API fails', () => {
    const fixture = TestBed.createComponent(ProcuradoriaPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/procuradoria').flush(
      { title: 'Error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar o workflow da Procuradoria',
    );
    http.verify();
  });
});
