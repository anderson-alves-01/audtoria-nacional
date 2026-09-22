import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { TransferReconciliationPageComponent } from './transfer-reconciliation-page.component';

describe('TransferReconciliationPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TransferReconciliationPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty transfer reconciliation shell', () => {
    const fixture = TestBed.createComponent(TransferReconciliationPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/transfer-reconciliation').flush({
      version: 'transfer-reconciliation-technical-v1',
      commandsDisabled: true,
      autoReconcileEnabled: false,
      createsTaxCredit: false,
      differenceIsOccurrenceOnly: true,
      g7Status: 'LOCAL_GO_OFFICIAL_BLOCKED',
      items: [],
      differences: [],
      disclaimer: 'Conciliação técnica de transferências vazia.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Conciliação de transferências');
    expect(text).toContain('LOCAL_GO_OFFICIAL_BLOCKED');
    expect(text).toContain('Sem crédito automático');
    http.verify();
  });

  it('shows error when reconciliation API fails', () => {
    const fixture = TestBed.createComponent(TransferReconciliationPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/transfer-reconciliation').flush(
      { title: 'Error' },
      { status: 500, statusText: 'Server Error' },
    );
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'Não foi possível carregar a conciliação de transferências',
    );
    http.verify();
  });
});
