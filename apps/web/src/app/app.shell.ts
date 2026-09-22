export const APP_IMPLEMENTATION_VERSION = '0.3.101';
export const APP_STATUS_LINE =
  'referência PUBLIC_OPEN · painéis oficiais · sem crédito';

export type NavItem = { path: string; label: string };

/** Os 15 painéis oficiais (mesmo componente DashboardPage). */
export const APP_DASHBOARD_NAV: NavItem[] = [
  { path: '/executivo', label: 'Executivo' },
  { path: '/financeiro', label: 'Financeiro' },
  { path: '/economia', label: 'Economia' },
  { path: '/operacao', label: 'Operação' },
  { path: '/achados', label: 'Achados' },
  { path: '/cobranca', label: 'Cobrança' },
  { path: '/pagamentos', label: 'Pagamentos' },
  { path: '/divida-ativa', label: 'Dívida ativa' },
  { path: '/transferencias', label: 'Transferências' },
  { path: '/ibs-cbs', label: 'IBS/CBS' },
  { path: '/qualidade', label: 'Qualidade' },
  { path: '/auditoria', label: 'Auditoria' },
  { path: '/gates', label: 'Gates' },
  { path: '/publico', label: 'Público' },
  { path: '/prontidao', label: 'Prontidão' },
];

/** Utilitários fora do catálogo dos 15. */
export const APP_UTILITY_NAV: NavItem[] = [
  { path: '/', label: 'Saúde' },
  { path: '/fontes', label: 'Fontes' },
  { path: '/setorial', label: 'Setorial' },
  { path: '/transferencias-estaduais', label: 'Estaduais' },
  { path: '/conciliacao-transferencias', label: 'Conciliação' },
  { path: '/diagnostico', label: 'Diagnóstico' },
  { path: '/regras-auditoria', label: 'Regras' },
  { path: '/casos-auditoria', label: 'Casos' },
  { path: '/notificacoes', label: 'Notificações' },
  { path: '/validacao', label: 'Validação' },
  { path: '/validacao-humana', label: 'Validação humana' },
  { path: '/cadastro-360', label: 'Cadastro 360' },
  { path: '/upload-municipal', label: 'Upload' },
  { path: '/funil', label: 'Funil' },
  { path: '/operacao-governanca', label: 'Ops' },
  { path: '/calendario', label: 'Calendário' },
];
