import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { TaxBetterAdminPageComponent } from './tax-better-admin-page.component';

function flushSession(http: HttpTestingController): void {
  http.expectOne('/v1/auth/public-open-session').flush({
    accessToken: 'token',
    territoryId: 'territory',
    purposeId: 'purpose',
    expiresAt: '2099-01-01T00:00:00Z',
    mode: 'PUBLIC_OPEN_UI_BOOTSTRAP',
  });
}

describe('TaxBetterAdminPageComponent', () => {
  beforeEach(async () => {
    sessionStorage.clear();
    await TestBed.configureTestingModule({
      imports: [TaxBetterAdminPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('shows the directory and keeps the public session from granting access', async () => {
    const fixture = TestBed.createComponent(TaxBetterAdminPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    flushSession(http);
    await fixture.whenStable();
    http.expectOne('/v1/admin/users').flush({
      createsTaxCredit: false,
      canManage: false,
      manageReason: 'A sessão de consulta não altera usuários nem acessos.',
      roles: [{ code: 'analyst', label: 'Analista' }],
      territories: [{ id: 't1', code: 'centro', name: 'Centro' }],
      purposes: [{ id: 'p1', code: 'audit-iss', description: 'Auditoria de referência' }],
      users: [
        {
          id: 'u1',
          username: 'analyst.alpha',
          role: 'analyst',
          roleLabel: 'Analista',
          active: true,
          territoryIds: ['t1'],
          createsTaxCredit: false,
        },
      ],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('analyst.alpha');
    expect(text).toContain('A sessão de consulta não altera usuários nem acessos.');
    expect(text).toContain('Criar usuário');
    expect(text).toContain('Cria crédito: não');
    const save = fixture.nativeElement.querySelector('button[type="submit"]') as HTMLButtonElement;
    expect(save.disabled).toBeTrue();
    http.verify();
  });

  it('creates a user without sending a password', async () => {
    const fixture = TestBed.createComponent(TaxBetterAdminPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    flushSession(http);
    await fixture.whenStable();
    http.expectOne('/v1/admin/users').flush({
      createsTaxCredit: false,
      canManage: true,
      manageReason: null,
      roles: [{ code: 'analyst', label: 'Analista' }],
      territories: [{ id: 't1', code: 'centro', name: 'Centro' }],
      purposes: [],
      users: [],
    });
    fixture.detectChanges();
    fixture.componentInstance.username = 'marina';
    fixture.componentInstance.role = 'analyst';
    fixture.componentInstance.territoryIds = ['t1'];
    fixture.detectChanges();
    const save = fixture.nativeElement.querySelector('button[type="submit"]') as HTMLButtonElement;
    save.click();
    const created = http.expectOne('/v1/admin/users');
    expect(created.request.method).toBe('POST');
    expect(created.request.body.username).toBe('marina');
    expect(created.request.body.password).toBeUndefined();
    expect(created.request.body.secret).toBeUndefined();
    created.flush({
      id: 'u2',
      username: 'marina',
      role: 'analyst',
      roleLabel: 'Analista',
      active: true,
      territoryIds: ['t1'],
      createsTaxCredit: false,
    });
    fixture.detectChanges();
    http.expectOne('/v1/admin/users').flush({
      createsTaxCredit: false,
      canManage: true,
      manageReason: null,
      roles: [{ code: 'analyst', label: 'Analista' }],
      territories: [{ id: 't1', code: 'centro', name: 'Centro' }],
      purposes: [],
      users: [],
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Nenhum crédito foi criado');
    http.verify();
  });
});
