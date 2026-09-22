import { Component, inject } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { PublicOpenSessionService } from '../auth/public-open-session.service';
import { APP_NAV_GROUPS, NavGroup } from './navigation';
import { humanizeContext, humanizeSessionMode } from '../shared/presentation/official-labels';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './app-shell.component.html',
  styleUrl: './app-shell.component.scss',
})
export class AppShellComponent {
  private readonly router = inject(Router);
  private readonly session = inject(PublicOpenSessionService);

  readonly groups = APP_NAV_GROUPS;
  collapsed = false;
  mobileOpen = false;
  query = '';
  breadcrumb = 'Visão executiva';
  groupLabel = 'Gestão Executiva da Receita';
  readonly expanded = new Set(APP_NAV_GROUPS.map((group) => group.id));

  constructor() {
    this.router.events.pipe(filter((event) => event instanceof NavigationEnd)).subscribe(() => {
      this.syncTrail();
      this.mobileOpen = false;
    });
    this.syncTrail();
  }

  get localBadge(): boolean {
    return typeof location !== 'undefined' && /localhost|127\.0\.0\.1/.test(location.hostname);
  }

  get territoryLabel(): string {
    return humanizeContext('territory', this.session.peek()?.territoryId);
  }

  get territoryCode(): string {
    return this.session.peek()?.territoryId || '';
  }

  get purposeLabel(): string {
    return humanizeContext('purpose', this.session.peek()?.purposeId);
  }

  get purposeCode(): string {
    return this.session.peek()?.purposeId || '';
  }

  get profileLabel(): string {
    return humanizeSessionMode(this.session.peek()?.mode);
  }

  visibleGroups(): NavGroup[] {
    const term = this.query.trim().toLowerCase();
    if (!term) {
      return this.groups;
    }
    return this.groups
      .map((group) => ({
        ...group,
        links: group.links.filter(
          (link) =>
            link.label.toLowerCase().includes(term) || link.path.toLowerCase().includes(term),
        ),
      }))
      .filter((group) => group.links.length > 0);
  }

  toggleGroup(id: string): void {
    if (this.expanded.has(id)) {
      this.expanded.delete(id);
    } else {
      this.expanded.add(id);
    }
  }

  private syncTrail(): void {
    let route = this.router.routerState.root;
    while (route.firstChild) {
      route = route.firstChild;
    }
    const title = route.snapshot.data['title'];
    const group = route.snapshot.data['group'];
    this.breadcrumb = typeof title === 'string' ? title : 'SIRTA';
    this.groupLabel = typeof group === 'string' ? group : 'SIRTA';
  }
}
