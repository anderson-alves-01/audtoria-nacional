import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { HumanValidationPageComponent } from './human-validation-page.component';

describe('HumanValidationPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HumanValidationPageComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('renders empty workflow without public credit', () => {
    const fixture = TestBed.createComponent(HumanValidationPageComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/v1/human-validation').flush({
      version: 'human-validation-workflow-v1',
      commandsDisabled: true,
      createsTaxCredit: false,
      publishesPublicCredit: false,
      g4Status: 'BLOCKED',
      g5Status: 'BLOCKED',
      referenceStates: ['IDENTIFIED', 'VALIDATED'],
      activeItems: [],
      queue: [],
      disclaimer: 'Workflow técnico de validação humana vazio.',
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Validação humana (workflow técnico)');
    expect(text).toContain('G4: BLOCKED');
    expect(text).toContain('Sem crédito público');
    expect(text).toContain('IDENTIFIED');
    http.verify();
  });
});
