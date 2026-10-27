/** Cores dos graficos lidas dos tokens do sistema de design (tema claro ou escuro). */
export interface ChartTheme {
  text: string;
  text2: string;
  muted: string;
  line: string;
  surface: string;
  accent: string;
  accentSoft: string;
  categorical: string[];
  sequential: string[];
  nullFill: string;
  fontUi: string;
  fontNum: string;
}

const FALLBACK: ChartTheme = {
  text: '#e6ecf5',
  text2: '#a5b4cc',
  muted: '#8496b4',
  line: '#24334f',
  surface: '#111a2c',
  accent: '#2dd4bf',
  accentSoft: 'rgba(45, 212, 191, 0.14)',
  categorical: ['#2dd4bf', '#6ea2ff', '#f5b942', '#ff8a70', '#a78bfa', '#4ade80', '#f472b6', '#94a3b8'],
  sequential: ['#12384a', '#136a77', '#1b9a9a', '#2dd4bf', '#b4f4e8'],
  nullFill: '#1a2640',
  fontUi: 'Inter, Segoe UI, system-ui, sans-serif',
  fontNum: 'JetBrains Mono, Cascadia Mono, monospace',
};

export function readChartTheme(): ChartTheme {
  if (typeof document === 'undefined' || typeof getComputedStyle !== 'function') {
    return FALLBACK;
  }
  const style = getComputedStyle(document.documentElement);
  const read = (name: string, fallback: string): string => {
    const value = style.getPropertyValue(name).trim();
    return value || fallback;
  };
  return {
    text: read('--text', FALLBACK.text),
    text2: read('--text-2', FALLBACK.text2),
    muted: read('--muted', FALLBACK.muted),
    line: read('--line', FALLBACK.line),
    surface: read('--surface', FALLBACK.surface),
    accent: read('--accent', FALLBACK.accent),
    accentSoft: read('--accent-soft', FALLBACK.accentSoft),
    categorical: FALLBACK.categorical.map((color, index) => read(`--d${index + 1}`, color)),
    sequential: FALLBACK.sequential.map((color, index) => read(`--seq-${index + 1}`, color)),
    nullFill: read('--null-fill', FALLBACK.nullFill),
    fontUi: read('--font-ui', FALLBACK.fontUi),
    fontNum: read('--font-num', FALLBACK.fontNum),
  };
}
