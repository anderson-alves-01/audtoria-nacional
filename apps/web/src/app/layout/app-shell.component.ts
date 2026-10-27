import { Component, HostListener, computed, inject, signal } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { PublicOpenSessionService } from '../auth/public-open-session.service';
import { humanizeContext } from '../shared/presentation/official-labels';
import { BadgeComponent } from '../shared/ui/badge.component';
import { ThemeService } from '../shared/ui/theme.service';
import { CommandPaletteComponent, PaletteItem } from './command-palette.component';
import { APP_NAV_GROUPS, NAV_ICONS, OPEN_NAV_GROUP_IDS, NavGroup } from './navigation';
import { WorkspaceTabsService } from './workspace-tabs.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet, CommandPaletteComponent, BadgeComponent],
  templateUrl: './app-shell.component.html',
  styleUrl: './app-shell.component.scss',
})
export class AppShellComponent {
  private readonly router = inject(Router);
  private readonly session = inject(PublicOpenSessionService);
  readonly themes = inject(ThemeService);
  readonly workspace = inject(WorkspaceTabsService);

  readonly groups = APP_NAV_GROUPS;
  readonly icons = NAV_ICONS;
  collapsed = false;
  mobileOpen = false;
  userMenuOpen = false;
  readonly paletteOpen = signal(false);
  readonly currentPath = signal('/');
  breadcrumb = 'Visão geral';
  groupLabel = 'Visão';
  readonly expanded = new Set(OPEN_NAV_GROUP_IDS);

  readonly paletteItems = computed<PaletteItem[]>(() => {
    const links = this.groups.flatMap((group) =>
      group.links.map((link) => ({ id: `go:${link.path}`, label: link.label, hint: group.label })),
    );
    const actions: PaletteItem[] = [
      {
        id: 'theme',
        label: this.themes.theme() === 'dark' ? 'Usar tema claro' : 'Usar tema escuro',
        hint: 'Aparência',
      },
      { id: 'leave', label: 'Sair da plataforma', hint: 'Conta' },
    ];
    return [...links, ...actions];
  });

  constructor() {
    this.router.events.pipe(filter((event) => event instanceof NavigationEnd)).subscribe(() => {
      this.syncTrail();
      this.mobileOpen = false;
      this.userMenuOpen = false;
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
    return this.session.peek()?.username || 'Sessão autenticada';
  }

  get initials(): string {
    return this.profileLabel.slice(0, 2).toUpperCase();
  }

  leave(): void {
    this.session.clearOperator();
    void this.router.navigateByUrl('/entrar');
  }

  groupIsOpen(group: NavGroup): boolean {
    return this.expanded.has(group.id);
  }

  toggleGroup(id: string): void {
    if (this.expanded.has(id)) {
      this.expanded.delete(id);
    } else {
      this.expanded.add(id);
    }
  }

  iconFor(id: string): string {
    return this.icons[id] ?? this.icons['reference'];
  }

  openPalette(): void {
    this.paletteOpen.set(true);
  }

  onPicked(id: string): void {
    this.paletteOpen.set(false);
    if (id === 'theme') {
      this.themes.toggle();
    } else if (id === 'leave') {
      this.leave();
    } else if (id.startsWith('go:')) {
      const path = id.slice(3);
      const group = this.groups.find((entry) => entry.links.some((link) => link.path === path));
      if (group) {
        this.expanded.add(group.id);
      }
      void this.router.navigateByUrl(path);
    }
  }

  closeTab(path: string, event: Event): void {
    event.preventDefault();
    event.stopPropagation();
    const next = this.workspace.close(path, this.currentPath());
    if (next) {
      void this.router.navigateByUrl(next);
    }
  }

  @HostListener('document:keydown', ['$event'])
  onGlobalKey(event: KeyboardEvent): void {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      this.paletteOpen.set(!this.paletteOpen());
    } else if (event.key === 'Escape') {
      this.userMenuOpen = false;
      this.mobileOpen = false;
    }
  }

  private syncTrail(): void {
    let route = this.router.routerState.root;
    while (route.firstChild) {
      route = route.firstChild;
    }
    const data = route.snapshot?.data ?? {};
    const title = data['title'];
    const group = data['group'];
    this.breadcrumb = typeof title === 'string' ? title : 'SIRTA';
    this.groupLabel = typeof group === 'string' ? group : 'SIRTA';
    const path = this.router.url.split(/[?#]/)[0] || '/';
    this.currentPath.set(path);
    if (path !== '/' && typeof title === 'string') {
      this.workspace.visit(path, title);
    }
  }
}
