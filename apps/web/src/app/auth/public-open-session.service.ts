import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export type PublicOpenSession = {
  accessToken: string;
  territoryId: string;
  purposeId: string;
  expiresAt: string;
  mode: string;
};

const STORAGE_KEY = 'sirta.publicOpenSession';

@Injectable({ providedIn: 'root' })
export class PublicOpenSessionService {
  private readonly http = inject(HttpClient);
  private session: PublicOpenSession | null = null;

  async ensureSession(): Promise<void> {
    const cached = this.readCache();
    if (cached && !this.isExpired(cached)) {
      this.session = cached;
      return;
    }
    const body = await firstValueFrom(
      this.http.get<{
        accessToken: string;
        territoryId: string;
        purposeId: string;
        expiresAt: string;
        mode: string;
      }>('/v1/auth/public-open-session'),
    );
    this.session = {
      accessToken: body.accessToken,
      territoryId: body.territoryId,
      purposeId: body.purposeId,
      expiresAt: body.expiresAt,
      mode: body.mode,
    };
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(this.session));
  }

  authHeaders(): Record<string, string> | null {
    if (!this.session || this.isExpired(this.session)) {
      return null;
    }
    return {
      Authorization: `Bearer ${this.session.accessToken}`,
      'X-Territory-Id': this.session.territoryId,
      'X-Purpose-Id': this.session.purposeId,
    };
  }

  peek(): PublicOpenSession | null {
    if (this.session && !this.isExpired(this.session)) {
      return this.session;
    }
    const cached = this.readCache();
    if (cached && !this.isExpired(cached)) {
      this.session = cached;
      return cached;
    }
    return null;
  }

  private readCache(): PublicOpenSession | null {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return null;
      }
      return JSON.parse(raw) as PublicOpenSession;
    } catch {
      return null;
    }
  }

  private isExpired(session: PublicOpenSession): boolean {
    const expires = Date.parse(session.expiresAt);
    if (Number.isNaN(expires)) {
      return true;
    }
    return expires <= Date.now() + 60_000;
  }
}
