import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import {
  APP_DASHBOARD_NAV,
  APP_IMPLEMENTATION_VERSION,
  APP_STATUS_LINE,
  APP_UTILITY_NAV,
} from './app.shell';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  readonly title = 'SIRTA Municipal';
  readonly implementationVersion = APP_IMPLEMENTATION_VERSION;
  readonly statusLine = APP_STATUS_LINE;
  readonly dashboardNav = APP_DASHBOARD_NAV;
  readonly utilityNav = APP_UTILITY_NAV;
}
