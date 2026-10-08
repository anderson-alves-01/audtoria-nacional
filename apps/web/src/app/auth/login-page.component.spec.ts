import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { LoginPageComponent } from './login-page.component';

@Component({ standalone: true, template: '' })
class DestinationPage {}

describe('LoginPageComponent', () => {
  beforeEach(async () => {
    sessionStorage.clear();
    await TestBed.configureTestingModule({
      imports: [LoginPageComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([{ path: 'visao', component: DestinationPage }]),
      ],
    }).compileComponents();
  });

  it('stores the operator session and does not keep the password on screen', () => {
    const fixture = TestBed.createComponent(LoginPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    fixture.componentInstance.username = 'admin.alpha';
    fixture.componentInstance.password = 'admin2026';
    fixture.detectChanges();
    const button = fixture.nativeElement.querySelector('button[type="submit"]') as HTMLButtonElement;
    button.click();
    const login = http.expectOne('/v1/auth/login');
    expect(login.request.body.username).toBe('admin.alpha');
    expect(login.request.body.password).toBe('admin2026');
    expect(login.request.body.code).toBeUndefined();
    login.flush({
      accessToken: 'token',
      expiresAt: '2099-01-01T00:00:00Z',
      territoryId: 'territory',
      purposeId: 'purpose',
      mode: 'OPERATOR_LOGIN',
      username: 'admin.alpha',
      createsTaxCredit: false,
    });
    fixture.detectChanges();
    expect(fixture.componentInstance.password).toBe('');
    expect(sessionStorage.getItem('sirta.operatorSession')).toContain('admin.alpha');
    expect(fixture.nativeElement.textContent).toContain('Entrar');
    expect(fixture.nativeElement.textContent).not.toContain('código do autenticador');
    expect(fixture.nativeElement.textContent).not.toContain('Nenhum acesso cria crédito');
    http.verify();
  });
});
