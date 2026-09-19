import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { StateTransfersPageComponent } from './state-transfers-page.component';

describe('StateTransfersPageComponent', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
  });

  it('renders PE and BA activated without inventing credit', () => {
    const fixture = TestBed.createComponent(StateTransfersPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/state-transfers').flush({
      version: 'state-transfers-technical-v1',
      ingestEnabled: true,
      createsTaxCredit: false,
      institutionalStatus: 'TECHNICALLY_APPROVED',
      verifiedCount: 4,
      states: [
        {
          uf: 'PE',
          name: 'Pernambuco',
          status: 'TECHNICALLY_APPROVED',
          structuredOfficialSource: 'ckan_csv_downloadable',
          ingestAllowed: true,
        },
        {
          uf: 'BA',
          name: 'Bahia',
          status: 'TECHNICALLY_APPROVED',
          structuredOfficialSource: 'ckan_csv_downloadable',
          ingestAllowed: true,
        },
        {
          uf: 'RJ',
          name: 'Rio de Janeiro',
          status: 'PROVENANCE_VERIFIED',
          structuredOfficialSource: 'ckan_csv_cataloged',
          ingestAllowed: false,
        },
      ],
      items: [],
      disclaimer: 'Catálogo estadual ICMS/IPVA.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Transferências estaduais ICMS/IPVA');
    expect(text).toContain('PE');
    expect(text).toContain('BA');
    expect(text).toContain('TECHNICALLY_APPROVED');
    expect(text).toContain('ingestAllowed=true');
    expect(text).toContain('Ingestão habilitada: sim');
    expect(text).toContain('Cria crédito: não');
    http.verify();
  });

  it('shows error when state transfers API fails', () => {
    const fixture = TestBed.createComponent(StateTransfersPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/state-transfers').flush(
      { detail: 'error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar as transferências estaduais',
    );
    http.verify();
  });
});
