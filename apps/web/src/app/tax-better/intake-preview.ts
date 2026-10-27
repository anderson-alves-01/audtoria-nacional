/**
 * Pre-visualizacao local do arquivo de entrada. Nada e gravado nem enviado: o servidor valida
 * de novo no registro. Segue a regra do leitor da API (cabecalho + virgula, todos os campos
 * mapeados obrigatorios por linha).
 */

export interface PreviewField {
  key: string;
  label: string;
}

export interface FieldCheck {
  key: string;
  label: string;
  column: string;
  status: 'ok' | 'sem-mapa' | 'sem-coluna';
}

export interface PreviewResult {
  headers: string[];
  rows: Record<string, string>[];
  totalRows: number;
  checks: FieldCheck[];
  /** Linhas com algum campo mapeado vazio: iriam para quarentena. */
  incompleteRows: number;
  error: string | null;
}

/** Leitor CSV pequeno: aspas duplas, virgula como separador, quebras de linha CRLF ou LF. */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = '';
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') {
        cell += '"';
        i += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        cell += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ',') {
      row.push(cell);
      cell = '';
    } else if (char === '\n' || char === '\r') {
      if (char === '\r' && text[i + 1] === '\n') {
        i += 1;
      }
      row.push(cell);
      cell = '';
      if (row.some((value) => value.trim() !== '')) {
        rows.push(row);
      }
      row = [];
    } else {
      cell += char;
    }
  }
  row.push(cell);
  if (row.some((value) => value.trim() !== '')) {
    rows.push(row);
  }
  return rows;
}

export function previewFile(
  text: string,
  fields: PreviewField[],
  fieldMap: Record<string, string>,
  limit = 10,
): PreviewResult {
  const table = parseCsv(text);
  if (table.length === 0) {
    return emptyResult(fields, fieldMap, 'Cole o arquivo com a linha de cabeçalho para ver a prévia.');
  }
  const headers = table[0].map((name) => name.trim());
  const records = table.slice(1).map((cells) => {
    const record: Record<string, string> = {};
    headers.forEach((name, index) => {
      record[name] = (cells[index] ?? '').trim();
    });
    return record;
  });
  return build(headers, records, fields, fieldMap, limit);
}

export function previewApi(
  body: string,
  fields: PreviewField[],
  fieldMap: Record<string, string>,
  limit = 10,
): PreviewResult {
  let parsed: unknown;
  try {
    parsed = JSON.parse(body || '[]');
  } catch {
    return emptyResult(fields, fieldMap, 'A resposta precisa ser uma lista JSON.');
  }
  if (!Array.isArray(parsed)) {
    return emptyResult(fields, fieldMap, 'A resposta precisa ser uma lista JSON.');
  }
  const records = parsed
    .filter((item): item is Record<string, unknown> => typeof item === 'object' && item !== null)
    .map((item) => Object.fromEntries(Object.entries(item).map(([key, value]) => [key, value == null ? '' : String(value).trim()])));
  const headers = [...new Set(records.flatMap((record) => Object.keys(record)))];
  return build(headers, records, fields, fieldMap, limit);
}

function emptyResult(fields: PreviewField[], fieldMap: Record<string, string>, error: string | null): PreviewResult {
  return {
    headers: [],
    rows: [],
    totalRows: 0,
    checks: checks(fields, fieldMap, []),
    incompleteRows: 0,
    error,
  };
}

function checks(fields: PreviewField[], fieldMap: Record<string, string>, headers: string[]): FieldCheck[] {
  return fields.map((field) => {
    const column = (fieldMap[field.key] ?? '').trim();
    let status: FieldCheck['status'] = 'ok';
    if (!column) {
      status = 'sem-mapa';
    } else if (!headers.includes(column)) {
      status = 'sem-coluna';
    }
    return { key: field.key, label: field.label, column, status };
  });
}

function build(
  headers: string[],
  records: Record<string, string>[],
  fields: PreviewField[],
  fieldMap: Record<string, string>,
  limit: number,
): PreviewResult {
  const fieldChecks = checks(fields, fieldMap, headers);
  const mapped = fieldChecks.filter((check) => check.column).map((check) => check.column);
  const incomplete = records.filter((record) => mapped.length < fields.length || mapped.some((column) => !record[column])).length;
  return {
    headers,
    rows: records.slice(0, limit),
    totalRows: records.length,
    checks: fieldChecks,
    incompleteRows: incomplete,
    error: null,
  };
}

export function previewIsReady(result: PreviewResult): boolean {
  return !result.error && result.totalRows > 0 && result.checks.every((check) => check.status === 'ok');
}
