import { Routes } from '@angular/router';
import { LoginPageComponent } from './auth/login-page.component';
import { loginGuard, operatorGuard } from './auth/operator.guard';
import { AppShellComponent } from './layout/app-shell.component';

const executive = 'Referência publicada';
const recovery = 'Referência publicada';
const transfers = 'Referência publicada';
const intelligence = 'Referência publicada';
const reform = 'Referência publicada';
const governance = 'Referência publicada';
const integration = 'Integração';
const vision = 'Visão';
const administration = 'Administração';

const shellRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'visao' },
  {
    path: 'visao',
    loadComponent: () => import('./tax-better/tax-better-vision-page.component').then((m) => m.TaxBetterVisionPageComponent),
    data: { title: 'Visão geral', group: vision },
  },
  {
    path: 'integracao',
    loadComponent: () => import('./tax-better/tax-better-integration-page.component').then((m) => m.TaxBetterIntegrationPageComponent),
    data: { title: 'Entrada e saída', group: integration },
  },
  {
    path: 'administracao',
    loadComponent: () => import('./tax-better/tax-better-admin-page.component').then((m) => m.TaxBetterAdminPageComponent),
    data: { title: 'Usuários e acessos', group: administration },
  },
  {
    path: 'executivo',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'executivo', title: 'Visão executiva', group: executive },
  },
  {
    path: 'financeiro',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'financeiro', title: 'Dinheiro do Município', group: executive },
  },
  {
    path: 'economia',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'economia', title: 'Economia', group: intelligence },
  },
  {
    path: 'operacao',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'operacao', title: 'Painel de operação', group: governance },
  },
  {
    path: 'achados',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'achados', title: 'Achados', group: recovery },
  },
  {
    path: 'cobranca',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'cobranca', title: 'Cobrança', group: recovery },
  },
  {
    path: 'pagamentos',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'pagamentos', title: 'Pagamentos e parcelamentos', group: recovery },
  },
  {
    path: 'divida-ativa',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'divida-ativa', title: 'Dívida ativa', group: recovery },
  },
  {
    path: 'transferencias',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'transferencias', title: 'Transferências federais', group: transfers },
  },
  {
    path: 'ibs-cbs',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'ibs-cbs', title: 'IBS/CBS', group: reform },
  },
  {
    path: 'qualidade',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'qualidade', title: 'Qualidade e lineage', group: intelligence },
  },
  {
    path: 'auditoria',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'auditoria', title: 'Auditoria', group: intelligence },
  },
  {
    path: 'gates',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'gates', title: 'Gates', group: governance },
  },
  {
    path: 'publico',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'publico', title: 'Painel público', group: executive },
  },
  {
    path: 'prontidao',
    loadComponent: () => import('./dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
    data: { dashboardId: 'prontidao', title: 'Prontidão', group: reform },
  },
  {
    path: 'validacao',
    loadComponent: () => import('./validation/validation-page.component').then((m) => m.ValidationPageComponent),
    data: { title: 'Créditos e validação', group: recovery },
  },
  {
    path: 'validacao-humana',
    loadComponent: () => import('./human-validation/human-validation-page.component').then((m) => m.HumanValidationPageComponent),
    data: { title: 'Validação humana', group: governance },
  },
  {
    path: 'notificacoes',
    loadComponent: () => import('./notifications/notifications-page.component').then((m) => m.NotificationsPageComponent),
    data: { title: 'Alertas e metas', group: executive },
  },
  { path: 'funil', loadComponent: () => import('./funnel/funnel-page.component').then((m) => m.FunnelPageComponent), data: { title: 'Funil de recuperação', group: executive } },
  { path: 'calendario', loadComponent: () => import('./calendar/calendar-page.component').then((m) => m.CalendarPageComponent), data: { title: 'Calendário', group: reform } },
  {
    path: 'diagnostico',
    loadComponent: () => import('./diagnosis/diagnosis-page.component').then((m) => m.DiagnosisPageComponent),
    data: { title: 'Diagnóstico', group: governance },
  },
  {
    path: 'regras-auditoria',
    loadComponent: () => import('./audit-rules/audit-rules-page.component').then((m) => m.AuditRulesPageComponent),
    data: { title: 'Regras de auditoria', group: intelligence },
  },
  {
    path: 'casos-auditoria',
    loadComponent: () => import('./audit-cases/audit-cases-page.component').then((m) => m.AuditCasesPageComponent),
    data: { title: 'Casos de auditoria', group: recovery },
  },
  { path: 'fontes', loadComponent: () => import('./sources/sources-page.component').then((m) => m.SourcesPageComponent), data: { title: 'Fontes', group: intelligence } },
  {
    path: 'operacao-governanca',
    loadComponent: () => import('./ops-governance/ops-governance-page.component').then((m) => m.OpsGovernancePageComponent),
    data: { title: 'Operação e auditoria técnica', group: governance },
  },
  {
    path: 'upload-municipal',
    loadComponent: () => import('./municipal-uploads/municipal-uploads-page.component').then((m) => m.MunicipalUploadsPageComponent),
    data: { title: 'Upload municipal', group: governance },
  },
  {
    path: 'cadastro-360',
    loadComponent: () => import('./cadastro-360/cadastro-360-page.component').then((m) => m.Cadastro360PageComponent),
    data: { title: 'Cadastro 360', group: intelligence },
  },
  {
    path: 'setorial',
    loadComponent: () => import('./sectoral-enrichment/sectoral-enrichment-page.component').then((m) => m.SectoralEnrichmentPageComponent),
    data: { title: 'Inteligência Setorial', group: intelligence },
  },
  {
    path: 'transferencias-estaduais',
    loadComponent: () => import('./state-transfers/state-transfers-page.component').then((m) => m.StateTransfersPageComponent),
    data: { title: 'ICMS/IPVA estadual', group: transfers },
  },
  {
    path: 'conciliacao-transferencias',
    loadComponent: () => import('./transfer-reconciliation/transfer-reconciliation-page.component').then((m) => m.TransferReconciliationPageComponent),
    data: { title: 'Conciliação', group: transfers },
  },
  {
    path: 'procuradoria',
    loadComponent: () => import('./procuradoria/procuradoria-page.component').then((m) => m.ProcuradoriaPageComponent),
    data: { title: 'Procuradoria', group: recovery },
  },
  {
    path: 'saude',
    loadComponent: () => import('./health/health-page.component').then((m) => m.HealthPageComponent),
    data: { title: 'Saúde da plataforma', group: governance },
  },
  { path: 'sobre', loadComponent: () => import('./layout/about-page.component').then((m) => m.AboutPageComponent), data: { title: 'Sobre', group: governance } },
  {
    path: 'erro',
    loadComponent: () => import('./layout/status-page.component').then((m) => m.StatusPageComponent),
    data: {
      code: '500',
      title: 'Falha ao apresentar a página',
      message: 'A interface não completou esta leitura. Tente novamente. Nenhum dado foi inventado.',
      group: governance,
    },
  },
  {
    path: 'indisponivel',
    loadComponent: () => import('./layout/status-page.component').then((m) => m.StatusPageComponent),
    data: {
      code: '503',
      title: 'Serviço temporariamente indisponível',
      message: 'A plataforma não confirmou disponibilidade. Aguarde e tente de novo, sem repetir carga.',
      group: governance,
    },
  },
  {
    path: '**',
    loadComponent: () => import('./layout/status-page.component').then((m) => m.StatusPageComponent),
    data: {
      code: '404',
      title: 'Página não encontrada',
      message: 'O endereço não corresponde a um módulo do SIRTA.',
      group: governance,
    },
  },
];

export const routes: Routes = [
  {
    path: 'entrar',
    component: LoginPageComponent,
    canActivate: [loginGuard],
  },
  {
    path: '',
    component: AppShellComponent,
    canActivate: [operatorGuard],
    children: shellRoutes,
  },
];
