import { Injectable } from '@angular/core';

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
  private session: PublicOpenSession | null = null;

  rememberOperator(session: PublicOpenSession): void {
    this.session = session;
    sessionStorage.setItem(OPERATOR_KEY, JSON.stringify(session));
  }

  clearOperator(): void {
    this.session = null;
    sessionStorage.removeItem(OPERATOR_KEY);
    sessionStorage.removeItem(STORAGE_KEY);
  }

  async ensureSession(): Promise<void> {
    return;
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
    const operator = this.session ?? this.readKey(OPERATOR_KEY);
    if (!operator || operator.mode !== 'OPERATOR_LOGIN' || this.isExpired(operator)) {
      return null;
    }
    this.session = operator;
    return operator;
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
