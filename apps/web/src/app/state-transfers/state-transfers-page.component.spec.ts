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

  it('renders empty state transfers shell without tax credit or ingest', () => {
    const fixture = TestBed.createComponent(StateTransfersPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/state-transfers').flush({
      version: 'state-transfers-technical-v1',
      ingestEnabled: false,
      createsTaxCredit: false,
      institutionalStatus: 'DISCOVERED',
      verifiedCount: 1,
      states: [
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
    expect(text).toContain('RJ');
    expect(text).toContain('PROVENANCE_VERIFIED');
    expect(text).toContain('Ingestão habilitada: não');
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
