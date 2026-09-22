import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { MunicipalUploadsPageComponent } from './municipal-uploads-page.component';

describe('MunicipalUploadsPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MunicipalUploadsPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty municipal upload slots with upload disabled', () => {
    const fixture = TestBed.createComponent(MunicipalUploadsPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/municipal-uploads').flush({
      version: 'municipal-uploads-technical-v1',
      uploadEnabled: false,
      g0Status: 'BLOCKED',
      slots: [
        {
          sourceId: 'MUNICIPAL-ISS-RESTRICTED',
          layoutVersion: 'municipal-iss-v1',
          uploadEnabled: false,
          quarantineRequired: true,
          tenantScoped: true,
          samplePresent: false,
          status: 'CREDENTIAL_REQUIRED',
        },
      ],
      items: [],
      disclaimer: 'Upload municipal controlado vazio.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Upload municipal restrito');
    expect(text).toContain('Upload habilitado: não');
    expect(text).toContain('MUNICIPAL-ISS-RESTRICTED');
    expect(text).toContain('BLOCKED');
    http.verify();
  });

  it('shows error when municipal uploads API fails', () => {
    const fixture = TestBed.createComponent(MunicipalUploadsPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/municipal-uploads').flush(
      { title: 'Error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar o upload municipal',
    );
    http.verify();
  });
});
