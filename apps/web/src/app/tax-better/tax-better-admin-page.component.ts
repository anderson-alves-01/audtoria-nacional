import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PublicOpenSessionService } from '../auth/public-open-session.service';
import { humanizeContext, humanizeSessionMode } from '../shared/presentation/official-labels';

interface RoleOption {
  code: string;
  label: string;
}

interface TerritoryOption {
  id: string;
  code: string;
  name: string;
}

interface PurposeOption {
  id: string;
  code: string;
  description: string;
}

interface UserRow {
  id: string;
  username: string;
  role: string;
  roleLabel: string;
  active: boolean;
  territoryIds: string[];
  createsTaxCredit: boolean;
}

interface Directory {
  createsTaxCredit: boolean;
  canManage: boolean;
  manageReason: string | null;
  roles: RoleOption[];
  territories: TerritoryOption[];
  purposes: PurposeOption[];
  users: UserRow[];
}

@Component({
  selector: 'app-tax-better-admin-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './tax-better-admin-page.component.html',
  styleUrl: './tax-better-page.scss',
})
export class TaxBetterAdminPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly session = inject(PublicOpenSessionService);
  state: 'loading' | 'ok' | 'error' = 'loading';
  directory: Directory | null = null;
  message = '';
  editingId: string | null = null;
  username = '';
  role = 'analyst';
  active = true;
  territoryIds: string[] = [];

  get territoryLabel(): string {
    return humanizeContext('territory', this.session.peek()?.territoryId);
  }

  get purposeLabel(): string {
    return humanizeContext('purpose', this.session.peek()?.purposeId);
  }

  get profileLabel(): string {
    return humanizeSessionMode(this.session.peek()?.mode);
  }

  ngOnInit(): void {
    void this.session.ensureSession().then(() => this.load()).catch(() => this.load());
  }

  load(): void {
    this.http.get<Directory>('/v1/admin/users').subscribe({
      next: (body) => {
        this.directory = {
          ...body,
          createsTaxCredit: false,
          users: body.users || [],
        };
        if (!this.role && body.roles?.length) {
          this.role = body.roles[0].code;
        }
        this.state = 'ok';
      },
      error: () => {
        this.message = 'O diretório de usuários não pôde ser lido.';
        this.state = 'error';
      },
    });
  }

  territoryChecked(id: string): boolean {
    return this.territoryIds.includes(id);
  }

  toggleTerritory(id: string, checked: boolean): void {
    if (checked) {
      this.territoryIds = [...new Set([...this.territoryIds, id])];
      return;
    }
    this.territoryIds = this.territoryIds.filter((item) => item !== id);
  }

  edit(user: UserRow): void {
    this.editingId = user.id;
    this.username = user.username;
    this.role = user.role;
    this.active = user.active;
    this.territoryIds = [...user.territoryIds];
    this.message = '';
  }

  resetForm(): void {
    this.editingId = null;
    this.username = '';
    this.role = this.directory?.roles[0]?.code || 'analyst';
    this.active = true;
    this.territoryIds = [];
  }

  save(): void {
    if (!this.directory?.canManage) {
      return;
    }
    const body = {
      username: this.username,
      role: this.role,
      active: this.active,
      territoryIds: this.territoryIds,
    };
    const request = this.editingId
      ? this.http.put<UserRow>(`/v1/admin/users/${this.editingId}`, body)
      : this.http.post<UserRow>('/v1/admin/users', body);
    request.subscribe({
      next: (saved) => {
        this.message = saved.active
          ? `Acesso de ${saved.username} gravado. Nenhum crédito foi criado.`
          : `Acesso de ${saved.username} encerrado. Nenhum crédito foi criado.`;
        this.resetForm();
        this.load();
      },
      error: () => {
        this.message = 'O acesso não foi gravado. Confira o papel, o território e a permissão da sessão.';
      },
    });
  }

  deactivate(user: UserRow): void {
    if (!this.directory?.canManage) {
      return;
    }
    this.http.delete<UserRow>(`/v1/admin/users/${user.id}`).subscribe({
      next: () => {
        this.message = `Acesso de ${user.username} encerrado. Nenhum crédito foi criado.`;
        this.load();
      },
      error: () => {
        this.message = 'O acesso não foi encerrado.';
      },
    });
  }

  territoryNames(user: UserRow): string {
    const names = (this.directory?.territories || [])
      .filter((item) => user.territoryIds.includes(item.id))
      .map((item) => item.name);
    return names.length ? names.join(', ') : '—';
  }
}
