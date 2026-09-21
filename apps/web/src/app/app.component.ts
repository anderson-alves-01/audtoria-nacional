import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import {
  APP_IMPLEMENTATION_VERSION,
  APP_NAV_GROUPS,
  APP_STATUS_LINE,
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
  readonly navGroups = APP_NAV_GROUPS;
}
