import { Injectable, signal } from '@angular/core';

export type ThemeName = 'dark' | 'light';

const STORAGE_KEY = 'sirta.theme';

/** Tema claro ou escuro. A escolha fica no navegador e vale para toda a plataforma. */
@Injectable({ providedIn: 'root' })
export class ThemeService {
  readonly theme = signal<ThemeName>(this.initial());

  toggle(): void {
    this.set(this.theme() === 'dark' ? 'light' : 'dark');
  }

  set(name: ThemeName): void {
    this.theme.set(name);
    document.documentElement.setAttribute('data-theme', name);
    try {
      localStorage.setItem(STORAGE_KEY, name);
    } catch {
      /* armazenamento indisponivel: o tema vale so nesta sessao */
    }
  }

  private initial(): ThemeName {
    const applied = document.documentElement.getAttribute('data-theme');
    if (applied === 'light' || applied === 'dark') {
      return applied;
    }
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'light' || saved === 'dark') {
        return saved;
      }
    } catch {
      /* sem armazenamento */
    }
    const light =
      typeof matchMedia === 'function' && matchMedia('(prefers-color-scheme: light)').matches;
    return light ? 'light' : 'dark';
  }
}
