export interface NavLink {
  path: string;
  label: string;
  exact?: boolean;
}

export interface NavGroup {
  id: string;
  label: string;
  links: NavLink[];
}

/** Menu vigente do Tax Better. As URLs já publicadas continuam no grupo recolhido. */
export const APP_NAV_GROUPS: NavGroup[] = [
  {
    id: 'integracao',
    label: 'Integração',
    links: [{ path: '/integracao', label: 'Entrada e saída' }],
  },
  {
    id: 'visao',
    label: 'Visão',
    links: [{ path: '/visao', label: 'Visão geral' }],
  },
  {
    id: 'administracao',
    label: 'Administração',
    links: [{ path: '/administracao', label: 'Usuários e acessos' }],
  },
  {
    id: 'reference',
    label: 'Referência publicada',
    links: [
      { path: '/executivo', label: 'Visão executiva' },
      { path: '/financeiro', label: 'Dinheiro do Município' },
      { path: '/funil', label: 'Funil de recuperação' },
      { path: '/notificacoes', label: 'Alertas e metas' },
      { path: '/publico', label: 'Painel público' },
      { path: '/validacao', label: 'Créditos e validação' },
      { path: '/achados', label: 'Achados' },
      { path: '/casos-auditoria', label: 'Casos de auditoria' },
      { path: '/cobranca', label: 'Cobrança' },
      { path: '/pagamentos', label: 'Pagamentos e parcelamentos' },
      { path: '/divida-ativa', label: 'Dívida ativa' },
      { path: '/procuradoria', label: 'Procuradoria' },
      { path: '/transferencias', label: 'Transferências federais' },
      { path: '/transferencias-estaduais', label: 'ICMS/IPVA estadual' },
      { path: '/conciliacao-transferencias', label: 'Conciliação' },
      { path: '/cadastro-360', label: 'Cadastro 360' },
      { path: '/economia', label: 'Economia' },
      { path: '/setorial', label: 'Inteligência Setorial' },
      { path: '/fontes', label: 'Fontes' },
      { path: '/qualidade', label: 'Qualidade e lineage' },
      { path: '/regras-auditoria', label: 'Regras de auditoria' },
      { path: '/auditoria', label: 'Auditoria' },
      { path: '/ibs-cbs', label: 'IBS/CBS' },
      { path: '/calendario', label: 'Calendário' },
      { path: '/prontidao', label: 'Prontidão' },
      { path: '/diagnostico', label: 'Diagnóstico' },
      { path: '/gates', label: 'Gates' },
      { path: '/validacao-humana', label: 'Validação humana' },
      { path: '/upload-municipal', label: 'Upload municipal' },
      { path: '/operacao-governanca', label: 'Operação e auditoria técnica' },
      { path: '/operacao', label: 'Painel de operação' },
      { path: '/saude', label: 'Saúde da plataforma' },
      { path: '/sobre', label: 'Sobre' },
    ],
  },
];

export const OPEN_NAV_GROUP_IDS = ['integracao', 'visao', 'administracao'];

export const APP_IMPLEMENTATION_VERSION = '0.4.0';
export const APP_STATUS_LINE = 'Tax Better · visão sem crédito';
