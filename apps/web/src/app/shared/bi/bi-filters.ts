import { DestroyRef, effect, inject, untracked } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { signal } from '@angular/core';
import { FilterChip } from '../ui/filter-bar.component';

const SEP = '~';
const PREFIX = 'f.';

export type DimensionValues = Record<string, string | null | undefined>;

/**
 * Estado de filtros de uma tela de BI: selecao cruzada por dimensao, caminho de detalhamento
 * (drill) e periodo. Tudo vive na URL para a visao poder ser compartilhada.
 */
export class BiFilters {
  readonly selections = signal<Record<string, string[]>>({});
  /** Valores escolhidos em cada nivel da hierarquia de detalhamento, do mais alto ao mais baixo. */
  readonly drillPath = signal<string[]>([]);

  constructor(readonly levels: string[] = []) {}

  /** Dimensao do nivel atual do detalhamento; null depois do ultimo nivel. */
  get currentLevel(): string | null {
    return this.levels[this.drillPath().length] ?? null;
  }

  isSelected(dimension: string, value: string): boolean {
    return (this.selections()[dimension] ?? []).includes(value);
  }

  /** Clique em um valor: alterna a selecao. Com `multi` falso substitui as demais. */
  toggle(dimension: string, value: string, multi = false): void {
    const current = this.selections()[dimension] ?? [];
    let next: string[];
    if (current.includes(value)) {
      next = current.filter((entry) => entry !== value);
    } else {
      next = multi ? [...current, value] : [value];
    }
    this.setDimension(dimension, next);
  }

  setDimension(dimension: string, values: string[]): void {
    const copy = { ...this.selections() };
    if (values.length === 0) {
      delete copy[dimension];
    } else {
      copy[dimension] = values;
    }
    this.selections.set(copy);
  }

  remove(key: string): void {
    if (key === 'drill') {
      this.drillPath.set([]);
      return;
    }
    this.setDimension(key, []);
  }

  clear(): void {
    this.selections.set({});
    this.drillPath.set([]);
  }

  drillInto(value: string): void {
    if (this.currentLevel !== null) {
      this.drillPath.set([...this.drillPath(), value]);
    }
  }

  drillUp(): void {
    this.drillPath.set(this.drillPath().slice(0, -1));
  }

  /** Verdadeiro quando a linha passa pelo detalhamento e por todas as selecoes. */
  matches(row: DimensionValues, skipDimension?: string): boolean {
    const path = this.drillPath();
    for (let i = 0; i < path.length; i += 1) {
      if ((row[this.levels[i]] ?? '') !== path[i]) {
        return false;
      }
    }
    for (const [dimension, values] of Object.entries(this.selections())) {
      if (dimension === skipDimension) {
        continue;
      }
      if (!values.includes(row[dimension] ?? '')) {
        return false;
      }
    }
    return true;
  }

  chips(labels: Record<string, string>): FilterChip[] {
    const chips: FilterChip[] = Object.entries(this.selections()).map(([dimension, values]) => ({
      key: dimension,
      label: labels[dimension] ?? dimension,
      value: values.join(', '),
    }));
    const path = this.drillPath();
    if (path.length > 0) {
      chips.unshift({
        key: 'drill',
        label: path.map((_, i) => labels[this.levels[i]] ?? this.levels[i]).join(' › '),
        value: path.join(' › '),
      });
    }
    return chips;
  }

  toParams(): Record<string, string | null> {
    const params: Record<string, string | null> = {};
    for (const [dimension, values] of Object.entries(this.selections())) {
      params[PREFIX + dimension] = values.join(SEP);
    }
    params['drill'] = this.drillPath().length > 0 ? this.drillPath().join(SEP) : null;
    return params;
  }

  load(read: (key: string) => string | null, keys: string[]): void {
    const selections: Record<string, string[]> = {};
    for (const key of keys) {
      if (key.startsWith(PREFIX)) {
        const raw = read(key);
        if (raw) {
          selections[key.slice(PREFIX.length)] = raw.split(SEP).filter(Boolean);
        }
      }
    }
    const drill = read('drill');
    this.selections.set(selections);
    this.drillPath.set(drill ? drill.split(SEP).filter(Boolean).slice(0, this.levels.length) : []);
  }

  serialize(): string {
    return JSON.stringify([this.selections(), this.drillPath()]);
  }
}

/** Mantem os filtros e a URL iguais nos dois sentidos. Chamar em contexto de injecao. */
export function syncFiltersWithUrl(filters: BiFilters, extraKeys: string[] = []): void {
  const route = inject(ActivatedRoute);
  const router = inject(Router);
  const destroy = inject(DestroyRef);
  let lastUrlState = '';

  const subscription = route.queryParamMap.subscribe((map) => {
    filters.load((key) => map.get(key), [...map.keys, ...extraKeys]);
    lastUrlState = filters.serialize();
  });
  destroy.onDestroy(() => subscription.unsubscribe());

  effect(() => {
    const state = filters.serialize();
    untracked(() => {
      if (state === lastUrlState) {
        return;
      }
      lastUrlState = state;
      const params = filters.toParams();
      // remove as chaves de filtro que sairam do estado
      for (const key of Object.keys(route.snapshot.queryParams)) {
        if (key.startsWith(PREFIX) && !(key in params)) {
          params[key] = null;
        }
      }
      void router.navigate([], {
        relativeTo: route,
        queryParams: params,
        queryParamsHandling: 'merge',
        replaceUrl: true,
      });
    });
  });
}
