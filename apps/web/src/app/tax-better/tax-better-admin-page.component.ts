import { Component, inject } from '@angular/core';
import { PublicOpenSessionService } from '../auth/public-open-session.service';
import { humanizeContext, humanizeSessionMode } from '../shared/presentation/official-labels';

@Component({
  selector: 'app-tax-better-admin-page',
  standalone: true,
  templateUrl: './tax-better-admin-page.component.html',
  styleUrl: './tax-better-page.scss',
})
export class TaxBetterAdminPageComponent {
  private readonly session = inject(PublicOpenSessionService);

  get territoryLabel(): string {
    return humanizeContext('territory', this.session.peek()?.territoryId);
  }

  get purposeLabel(): string {
    return humanizeContext('purpose', this.session.peek()?.purposeId);
  }

  get profileLabel(): string {
    return humanizeSessionMode(this.session.peek()?.mode);
  }
}
