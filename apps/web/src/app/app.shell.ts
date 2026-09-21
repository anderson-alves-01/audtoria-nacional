export const APP_IMPLEMENTATION_VERSION = '0.3.98';
export const APP_STATUS_LINE =
  'onda 1 oficial concluída · roadmap em progresso · homologação humana pendente';

export type NavItem = { path: string; label: string };
export type NavGroup = { id: string; label: string; items: NavItem[] };

/** Primary shell navigation grouped for scanning (public-sector ops UI). */
export const APP_NAV_GROUPS: NavGroup[] = [
  {
    id: 'visao',
    label: 'Visão',
    items: [
      { path: '/', label: 'Saúde' },
      { path: '/executivo', label: 'Executivo' },
      { path: '/financeiro', label: 'Financeiro' },
      { path: '/economia', label: 'Economia' },
      { path: '/operacao', label: 'Operação' },
    ],
  },
  {
    id: 'recuperacao',
    label: 'Recuperação',
    items: [
      { path: '/achados', label: 'Achados' },
      { path: '/casos-auditoria', label: 'Casos' },
      { path: '/notificacoes', label: 'Notificações' },
      { path: '/cobranca', label: 'Cobrança' },
      { path: '/pagamentos', label: 'Pagamentos' },
      { path: '/divida-ativa', label: 'Dívida ativa' },
      { path: '/procuradoria', label: 'Procuradoria' },
    ],
  },
  {
    id: 'transferencias',
    label: 'Transferências',
    items: [
      { path: '/transferencias', label: 'Transferências' },
      { path: '/conciliacao-transferencias', label: 'Conciliação' },
      { path: '/transferencias-estaduais', label: 'ICMS/IPVA estadual' },
      { path: '/ibs-cbs', label: 'IBS/CBS' },
    ],
  },
  {
    id: 'qualidade',
    label: 'Qualidade e auditoria',
    items: [
      { path: '/qualidade', label: 'Qualidade' },
      { path: '/auditoria', label: 'Auditoria' },
      { path: '/diagnostico', label: 'Diagnóstico' },
      { path: '/regras-auditoria', label: 'Regras' },
      { path: '/gates', label: 'Gates' },
      { path: '/validacao', label: 'Validação' },
      { path: '/validacao-humana', label: 'Validação humana' },
    ],
  },
  {
    id: 'dados',
    label: 'Dados e cadastro',
    items: [
      { path: '/fontes', label: 'Fontes' },
      { path: '/setorial', label: 'Setorial' },
      { path: '/cadastro-360', label: 'Cadastro 360' },
      { path: '/upload-municipal', label: 'Upload municipal' },
    ],
  },
  {
    id: 'programa',
    label: 'Programa',
    items: [
      { path: '/publico', label: 'Público' },
      { path: '/prontidao', label: 'Prontidão' },
      { path: '/funil', label: 'Funil' },
      { path: '/operacao-governanca', label: 'Ops' },
      { path: '/calendario', label: 'Calendário' },
    ],
  },
];
