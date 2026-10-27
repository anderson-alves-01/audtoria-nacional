import { ScrollingModule } from '@angular/cdk/scrolling';
import { NgTemplateOutlet } from '@angular/common';
import {
  Component,
  ContentChild,
  EventEmitter,
  Input,
  Output,
  TemplateRef,
  computed,
  signal,
} from '@angular/core';
import {
  BiColumn,
  Cell,
  EMPTY_CELL,
  SortState,
  displayCell,
  filterRows,
  formatCell,
  groupRows,
  sortRows,
  toCsv,
} from './table-logic';

type Line<T> =
  | { kind: 'group'; key: string; count: number; sums: Record<string, number | null>; open: boolean }
  | { kind: 'row'; row: T; index: number };

/**
 * Tabela de dados de BI: ordenar, filtrar por coluna, agrupar, redimensionar e ocultar colunas,
 * rolagem virtual, exportar CSV do que esta na tela e gaveta de detalhe da linha.
 */
@Component({
  selector: 'app-data-table',
  standalone: true,
  imports: [ScrollingModule, NgTemplateOutlet],
  templateUrl: './data-table.component.html',
  styleUrl: './data-table.component.scss',
})
export class DataTableComponent<T> {
  private readonly cols = signal<BiColumn<T>[]>([]);
  private readonly data = signal<T[]>([]);

  @Input({ required: true }) set columns(value: BiColumn<T>[]) {
    this.cols.set(value);
  }
  @Input({ required: true }) set rows(value: T[]) {
    this.data.set(value);
  }
  @Input() caption = 'Tabela de dados';
  @Input() exportName = 'dados';
  @Input() rowKey: (row: T) => string = (row) => JSON.stringify(row);
  @Output() rowSelected = new EventEmitter<T | null>();
  @ContentChild('detail') detail?: TemplateRef<{ $implicit: T }>;

  readonly sort = signal<SortState | null>(null);
  readonly filters = signal<Record<string, string>>({});
  readonly groupBy = signal<string>('');
  readonly hidden = signal<Set<string>>(new Set());
  readonly widths = signal<Record<string, number>>({});
  readonly collapsed = signal<Set<string>>(new Set());
  readonly selectedKey = signal<string | null>(null);
  readonly menuOpen = signal(false);
  readonly rowHeight = 36;

  readonly allRows = computed(() => this.data().length);
  readonly visibleColumns = computed(() => this.cols().filter((column) => !this.hidden().has(column.id)));
  readonly allColumns = computed(() => this.cols());

  readonly processed = computed(() => {
    const filtered = filterRows(this.data(), this.cols(), this.filters());
    return sortRows(filtered, this.cols(), this.sort());
  });

  readonly lines = computed<Line<T>[]>(() => {
    const rows = this.processed();
    const by = this.groupBy();
    if (!by) {
      return rows.map((row, index) => ({ kind: 'row', row, index }));
    }
    const out: Line<T>[] = [];
    let index = 0;
    for (const group of groupRows(rows, this.cols(), by)) {
      const open = !this.collapsed().has(group.key);
      out.push({ kind: 'group', key: group.key, count: group.count, sums: group.sums, open });
      if (open) {
        for (const row of group.rows) {
          out.push({ kind: 'row', row, index });
          index += 1;
        }
      }
    }
    return out;
  });

  readonly gridTemplate = computed(() =>
    this.visibleColumns()
      .map((column) => `${this.widths()[column.id] ?? column.width ?? 160}px`)
      .join(' '),
  );

  readonly selectedRow = computed(() => {
    const key = this.selectedKey();
    return key === null ? null : this.data().find((row) => this.rowKey(row) === key) ?? null;
  });

  trackLine = (_: number, line: Line<T>): string =>
    line.kind === 'group' ? `g:${line.key}` : `r:${this.rowKey(line.row)}`;

  ariaSort(column: BiColumn<T>): 'ascending' | 'descending' | 'none' {
    const sort = this.sort();
    if (!sort || sort.column !== column.id) {
      return 'none';
    }
    return sort.direction === 'asc' ? 'ascending' : 'descending';
  }

  toggleSort(column: BiColumn<T>): void {
    const sort = this.sort();
    if (!sort || sort.column !== column.id) {
      this.sort.set({ column: column.id, direction: 'asc' });
    } else if (sort.direction === 'asc') {
      this.sort.set({ column: column.id, direction: 'desc' });
    } else {
      this.sort.set(null);
    }
  }

  setFilter(id: string, value: string): void {
    this.filters.set({ ...this.filters(), [id]: value });
  }

  toggleColumn(id: string): void {
    const next = new Set(this.hidden());
    if (next.has(id)) {
      next.delete(id);
    } else if (this.visibleColumns().length > 1) {
      next.add(id);
    }
    this.hidden.set(next);
  }

  toggleGroup(key: string): void {
    const next = new Set(this.collapsed());
    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
    }
    this.collapsed.set(next);
  }

  select(row: T): void {
    const key = this.rowKey(row);
    const same = this.selectedKey() === key;
    this.selectedKey.set(same ? null : key);
    this.rowSelected.emit(same ? null : row);
  }

  cell(column: BiColumn<T>, row: T): string {
    return displayCell(column, row);
  }

  sumText(column: BiColumn<T>, sums: Record<string, number | null>): string {
    const value = sums[column.id];
    if (value === null || value === undefined) {
      return EMPTY_CELL;
    }
    return column.format ? column.format(value) : formatCell(value, true);
  }

  /** Redimensiona com o mouse ou com as setas quando a alca esta focada. */
  startResize(event: MouseEvent, column: BiColumn<T>): void {
    event.preventDefault();
    event.stopPropagation();
    const startX = event.clientX;
    const startWidth = this.widths()[column.id] ?? column.width ?? 160;
    const move = (e: MouseEvent): void => this.setWidth(column.id, startWidth + (e.clientX - startX));
    const up = (): void => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
    };
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
  }

  resizeKey(event: KeyboardEvent, column: BiColumn<T>): void {
    const step = event.shiftKey ? 40 : 12;
    const current = this.widths()[column.id] ?? column.width ?? 160;
    if (event.key === 'ArrowRight') {
      event.preventDefault();
      this.setWidth(column.id, current + step);
    } else if (event.key === 'ArrowLeft') {
      event.preventDefault();
      this.setWidth(column.id, current - step);
    }
  }

  private setWidth(id: string, width: number): void {
    this.widths.set({ ...this.widths(), [id]: Math.max(70, Math.min(640, Math.round(width))) });
  }

  exportCsv(): void {
    const csv = toCsv(this.processed(), this.visibleColumns());
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${this.exportName}.csv`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  numeric(column: BiColumn<T>): boolean {
    return !!column.numeric;
  }

  rawValue(column: BiColumn<T>, row: T): Cell {
    return column.value(row);
  }
}
