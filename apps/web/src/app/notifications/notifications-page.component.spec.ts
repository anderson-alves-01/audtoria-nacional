import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { NotificationsPageComponent } from './notifications-page.component';

describe('NotificationsPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NotificationsPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty notifications and surfaces rejected send', () => {
    const fixture = TestBed.createComponent(NotificationsPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/notifications').flush({
      catalogVersion: 'notifications-technical-v1',
      g5Status: 'BLOCKED',
      items: [],
      disclaimer: 'Notificações administrativas técnicas vazias.',
      sendEnabled: false,
      commandsDisabled: true,
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Notificações administrativas técnicas');
    expect(text).toContain('G5: BLOCKED');
    expect(text).toContain('Envio desativado');

    fixture.componentInstance.attemptSend();
    const send = http.expectOne('/v1/notifications');
    expect(send.request.method).toBe('POST');
    send.flush(
      { title: 'Conflict', detail: 'Envio desativado' },
      { status: 409, statusText: 'Conflict' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Envio recusado');
    http.verify();
  });
});
