import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { AuditCasesPageComponent } from './audit-cases-page.component';

describe('AuditCasesPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AuditCasesPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty cases and surfaces rejected create', () => {
    const fixture = TestBed.createComponent(AuditCasesPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/cases').flush({
      catalogVersion: 'audit-cases-technical-v1',
      g5Status: 'BLOCKED',
      items: [],
      disclaimer: 'Casos de auditoria técnicos vazios.',
      commandsDisabled: true,
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Casos de auditoria técnicos');
    expect(text).toContain('G5: BLOCKED');
    expect(text).toContain('Comandos desativados');

    fixture.componentInstance.attemptCreate();
    const create = http.expectOne('/v1/cases');
    expect(create.request.method).toBe('POST');
    create.flush(
      { title: 'Conflict', detail: 'Criação desativada' },
      { status: 409, statusText: 'Conflict' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Criação recusada');
    http.verify();
  });
});
