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

/** Única configuração de navegação. URLs existentes são preservadas. */
export const APP_NAV_GROUPS: NavGroup[] = [
  {
    id: "executive",
    label: "Gestão Executiva da Receita",
    links: [
      { path: "/executivo", label: "Visão executiva" },
      { path: "/financeiro", label: "Dinheiro do Município" },
      { path: "/funil", label: "Funil de recuperação" },
      { path: "/notificacoes", label: "Alertas e metas" },
      { path: "/publico", label: "Painel público" },
    ],
  },
  {
    id: "recovery",
    label: "Recuperação Tributária",
    links: [
      { path: "/validacao", label: "Créditos e validação" },
      { path: "/achados", label: "Achados" },
      { path: "/casos-auditoria", label: "Casos de auditoria" },
      { path: "/cobranca", label: "Cobrança" },
      { path: "/pagamentos", label: "Pagamentos e parcelamentos" },
      { path: "/divida-ativa", label: "Dívida ativa" },
      { path: "/procuradoria", label: "Procuradoria" },
    ],
  },
  {
    id: "transfers",
    label: "Auditoria de Repasses",
    links: [
      { path: "/transferencias", label: "Transferências federais" },
      { path: "/transferencias-estaduais", label: "ICMS/IPVA estadual" },
      { path: "/conciliacao-transferencias", label: "Conciliação" },
    ],
  },
  {
    id: "intelligence",
    label: "Inteligência Fiscal",
    links: [
      { path: "/cadastro-360", label: "Cadastro 360" },
      { path: "/economia", label: "Economia" },
      { path: "/setorial", label: "Inteligência Setorial" },
      { path: "/fontes", label: "Fontes" },
      { path: "/qualidade", label: "Qualidade e lineage" },
      { path: "/regras-auditoria", label: "Regras de auditoria" },
      { path: "/auditoria", label: "Auditoria" },
    ],
  },
  {
    id: "reform",
    label: "Observatório da Reforma Tributária",
    links: [
      { path: "/ibs-cbs", label: "IBS/CBS" },
      { path: "/calendario", label: "Calendário" },
      { path: "/prontidao", label: "Prontidão" },
    ],
  },
  {
    id: "governance",
    label: "Governança e Operação",
    links: [
      { path: "/diagnostico", label: "Diagnóstico" },
      { path: "/gates", label: "Gates" },
      { path: "/validacao-humana", label: "Validação humana" },
      { path: "/upload-municipal", label: "Upload municipal" },
      { path: "/operacao-governanca", label: "Operação e auditoria técnica" },
      { path: "/operacao", label: "Painel de operação" },
      { path: "/saude", label: "Saúde da plataforma" },
      { path: "/sobre", label: "Sobre" },
    ],
  },
];

export const APP_IMPLEMENTATION_VERSION = "0.4.0";
export const APP_STATUS_LINE = "referência PUBLIC_OPEN · painéis oficiais · sem crédito";
