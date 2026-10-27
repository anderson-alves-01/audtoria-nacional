import { parseCsv, previewApi, previewFile, previewIsReady } from './intake-preview';

const fields = [
  { key: 'organ', label: 'Órgão' },
  { key: 'tax', label: 'Imposto' },
];

describe('intake preview', () => {
  it('reads quoted cells and CRLF lines', () => {
    expect(parseCsv('a,b\r\n"x, y",2\r\n')).toEqual([
      ['a', 'b'],
      ['x, y', '2'],
    ]);
  });

  it('flags mapped columns that the file does not have', () => {
    const result = previewFile('orgao,imposto\nDETRAN,ICMS\n', fields, { organ: 'orgao', tax: 'tributo' });
    expect(result.checks.map((check) => check.status)).toEqual(['ok', 'sem-coluna']);
    expect(previewIsReady(result)).toBeFalse();
  });

  it('counts rows with an empty mapped field as quarantine candidates', () => {
    const result = previewFile('orgao,imposto\nDETRAN,ICMS\nDETRAN,\n', fields, { organ: 'orgao', tax: 'imposto' });
    expect(result.totalRows).toBe(2);
    expect(result.incompleteRows).toBe(1);
    expect(previewIsReady(result)).toBeTrue();
  });

  it('rejects an API body that is not a list and never invents rows', () => {
    const result = previewApi('{"a":1}', fields, { organ: 'orgao', tax: 'imposto' });
    expect(result.error).toContain('lista JSON');
    expect(result.totalRows).toBe(0);
  });

  it('reads an API list through the same map', () => {
    const result = previewApi('[{"orgao":"X","imposto":"ISS"}]', fields, { organ: 'orgao', tax: 'imposto' });
    expect(result.totalRows).toBe(1);
    expect(previewIsReady(result)).toBeTrue();
  });
});
