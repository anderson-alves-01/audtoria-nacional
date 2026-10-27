/** Regras puras da tabela de dados: ordenar, filtrar, agrupar e exportar. Nulo nunca vira zero. */

export type Cell = string | number | null;

export interface BiColumn<T> {
  id: string;
  label: string;
  value: (row: T) => Cell;
  numeric?: boolean;
  /** Texto exibido; sem formatador, numero usa pt-BR e nulo vira traço. */
  format?: (value: Cell) => string;
  width?: number;
}

export interface SortState {
  column: string;
  direction: 'asc' | 'desc';
}

export const EMPTY_CELL = '—';

export function formatCell(value: Cell, numeric = false): string {
  if (value === null || value === undefined || value === '') {
    return EMPTY_CELL;
  }
  if (typeof value === 'number') {
    return Number.isFinite(value)
      ? value.toLocaleString('pt-BR', { maximumFractionDigits: numeric ? 2 : 6 })
      : EMPTY_CELL;
  }
  return value;
}

export function displayCell<T>(column: BiColumn<T>, row: T): string {
  const value = column.value(row);
  return column.format ? column.format(value) : formatCell(value, column.numeric);
}

export function filterRows<T>(
  rows: T[],
  columns: BiColumn<T>[],
  filters: Record<string, string>,
): T[] {
  const active = Object.entries(filters).filter(([, term]) => term.trim() !== '');
  if (active.length === 0) {
    return rows;
  }
  return rows.filter((row) =>
    active.every(([id, term]) => {
      const column = columns.find((entry) => entry.id === id);
      if (!column) {
        return true;
      }
      return displayCell(column, row).toLowerCase().includes(term.trim().toLowerCase());
    }),
  );
}

export function sortRows<T>(rows: T[], columns: BiColumn<T>[], sort: SortState | null): T[] {
  if (!sort) {
    return rows;
  }
  const column = columns.find((entry) => entry.id === sort.column);
  if (!column) {
    return rows;
  }
  const factor = sort.direction === 'asc' ? 1 : -1;
  return [...rows].sort((left, right) => {
    const a = column.value(left);
    const b = column.value(right);
    if (a === null && b === null) {
      return 0;
    }
    // Nulos ficam sempre por ultimo, em qualquer sentido.
    if (a === null) {
      return 1;
    }
    if (b === null) {
      return -1;
    }
    if (typeof a === 'number' && typeof b === 'number') {
      return (a - b) * factor;
    }
    return String(a).localeCompare(String(b), 'pt-BR') * factor;
  });
}

export interface GroupRow<T> {
  key: string;
  count: number;
  /** Soma so dos valores existentes; sem nenhum valor a soma fica nula. */
  sums: Record<string, number | null>;
  rows: T[];
}

export function groupRows<T>(rows: T[], columns: BiColumn<T>[], by: string): GroupRow<T>[] {
  const column = columns.find((entry) => entry.id === by);
  if (!column) {
    return [];
  }
  const groups = new Map<string, GroupRow<T>>();
  for (const row of rows) {
    const key = displayCell(column, row);
    let group = groups.get(key);
    if (!group) {
      group = { key, count: 0, sums: {}, rows: [] };
      for (const entry of columns) {
        if (entry.numeric) {
          group.sums[entry.id] = null;
        }
      }
      groups.set(key, group);
    }
    group.count += 1;
    group.rows.push(row);
    for (const entry of columns) {
      if (!entry.numeric) {
        continue;
      }
      const value = entry.value(row);
      if (typeof value === 'number' && Number.isFinite(value)) {
        group.sums[entry.id] = (group.sums[entry.id] ?? 0) + value;
      }
    }
  }
  return [...groups.values()].sort((left, right) => left.key.localeCompare(right.key, 'pt-BR'));
}

/** CSV do que esta na tela, separado por ponto e virgula e com BOM para abrir bem no Excel. */
export function toCsv<T>(rows: T[], columns: BiColumn<T>[]): string {
  const escape = (text: string): string =>
    /[;"\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  const head = columns.map((column) => escape(column.label)).join(';');
  const lines = rows.map((row) => columns.map((column) => escape(displayCell(column, row))).join(';'));
  return '\ufeff' + [head, ...lines].join('\r\n');
}
