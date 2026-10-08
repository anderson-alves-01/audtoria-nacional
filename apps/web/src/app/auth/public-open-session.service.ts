import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export type PublicOpenSession = {
  accessToken: string;
  territoryId: string;
  purposeId: string;
  expiresAt: string;
  mode: string;
  username?: string;
};

const STORAGE_KEY = 'sirta.publicOpenSession';
const OPERATOR_KEY = 'sirta.operatorSession';

@Injectable({ providedIn: 'root' })
export class PublicOpenSessionService {
  private readonly http = inject(HttpClient);
  private session: PublicOpenSession | null = null;
  private operator: PublicOpenSession | null = null;

  rememberOperator(session: PublicOpenSession): void {
    this.operator = session;
    sessionStorage.setItem(OPERATOR_KEY, JSON.stringify(session));
  }

  clearOperator(): void {
    this.operator = null;
    sessionStorage.removeItem(OPERATOR_KEY);
  }

  async ensureSession(): Promise<void> {
    const cached = this.readKey(STORAGE_KEY);
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
    const current = this.peek();
    if (!current) {
      return null;
    }
    return {
      Authorization: `Bearer ${current.accessToken}`,
      'X-Territory-Id': current.territoryId,
      'X-Purpose-Id': current.purposeId,
    };
  }

  peek(): PublicOpenSession | null {
    const operator = this.operator ?? this.readKey(OPERATOR_KEY);
    if (operator && !this.isExpired(operator)) {
      this.operator = operator;
      return operator;
    }
    if (this.session && !this.isExpired(this.session)) {
      return this.session;
    }
    const cached = this.readKey(STORAGE_KEY);
    if (cached && !this.isExpired(cached)) {
      this.session = cached;
      return cached;
    }
    return null;
  }

  private readKey(key: string): PublicOpenSession | null {
    try {
      const raw = sessionStorage.getItem(key);
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
