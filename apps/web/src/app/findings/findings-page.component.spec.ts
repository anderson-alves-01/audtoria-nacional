import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { FindingsPageComponent } from './findings-page.component';

describe('FindingsPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FindingsPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty findings without creating credit language', () => {
    const fixture = TestBed.createComponent(FindingsPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/findings').flush({
      catalogVersion: 'findings-technical-v1',
      binding: false,
      operational: false,
      homologated: false,
      commandsDisabled: true,
      createsTaxCredit: false,
      legalCommandsEnabled: false,
      g5Status: 'BLOCKED',
      items: [],
      total: 0,
      disclaimer: 'Achados técnicos vazios. Comandos jurídicos desativados.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Achados de auditoria técnicos');
    expect(text).toContain('G5: BLOCKED');
    expect(text).toContain('Comandos desativados');
    expect(text).toContain('Não constitui crédito');
    http.verify();
  });
});
