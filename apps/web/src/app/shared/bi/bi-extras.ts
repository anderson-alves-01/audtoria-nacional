/** Filtros salvos e comparacao entre competencias. Nada aqui calcula tributo nem estima valor. */

export interface SavedView {
  name: string;
  params: Record<string, string | null>;
}

/** Visoes salvas no navegador por tela. Guardam so filtros, nunca linhas de dados. */
export class SavedViews {
  constructor(private readonly screen: string) {}

  private get key(): string {
    return `sirta.views.${this.screen}`;
  }

  list(): SavedView[] {
    try {
      const raw = localStorage.getItem(this.key);
      return raw ? (JSON.parse(raw) as SavedView[]) : [];
    } catch {
      return [];
    }
  }

  save(name: string, params: Record<string, string | null>): SavedView[] {
    const clean = name.trim();
    if (!clean) {
      return this.list();
    }
    const next = [...this.list().filter((view) => view.name !== clean), { name: clean, params }];
    this.write(next);
    return next;
  }

  remove(name: string): SavedView[] {
    const next = this.list().filter((view) => view.name !== name);
    this.write(next);
    return next;
  }

  private write(views: SavedView[]): void {
    try {
      localStorage.setItem(this.key, JSON.stringify(views));
    } catch {
      /* sem armazenamento: a visao vale so nesta sessao */
    }
  }
}

export interface Comparison {
  category: string;
  current: number | null;
  previous: number | null;
  /** Diferenca absoluta; nula se faltar qualquer um dos lados. */
  delta: number | null;
  /** Variacao percentual; nula se faltar um lado ou se a base for zero. */
  deltaPct: number | null;
}

/** Compara duas competencias por categoria. Lado ausente fica nulo e nao vira zero. */
export function compareSeries(
  categories: string[],
  current: Map<string, number | null>,
  previous: Map<string, number | null>,
): Comparison[] {
  return categories.map((category) => {
    const now = current.get(category) ?? null;
    const before = previous.get(category) ?? null;
    const both = now !== null && before !== null;
    return {
      category,
      current: now,
      previous: before,
      delta: both ? now - before : null,
      deltaPct: both && before !== 0 ? ((now - before) / Math.abs(before)) * 100 : null,
    };
  });
}
