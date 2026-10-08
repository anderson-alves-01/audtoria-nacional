import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { TaxBetterAdminPageComponent } from './tax-better-admin-page.component';

describe('TaxBetterAdminPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TaxBetterAdminPageComponent],
      providers: [provideHttpClient()],
    }).compileComponents();
  });

  it('shows the session and does not grant a role', () => {
    const fixture = TestBed.createComponent(TaxBetterAdminPageComponent);
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Usuários, acessos e papéis aguardam o ato');
    expect(text).toContain('não concede acesso');
    expect(text).not.toContain('Criar usuário');
    expect(fixture.nativeElement.querySelector('button')).toBeNull();
  });
});
