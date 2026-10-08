import { Routes } from '@angular/router';
import { LoginPageComponent } from './auth/login-page.component';
import { AuditCasesPageComponent } from './audit-cases/audit-cases-page.component';
import { AuditRulesPageComponent } from './audit-rules/audit-rules-page.component';
import { Cadastro360PageComponent } from './cadastro-360/cadastro-360-page.component';
import { CalendarPageComponent } from './calendar/calendar-page.component';
import { DashboardPageComponent } from './dashboard/dashboard-page.component';
import { DiagnosisPageComponent } from './diagnosis/diagnosis-page.component';
import { FunnelPageComponent } from './funnel/funnel-page.component';
import { HealthPageComponent } from './health/health-page.component';
import { HumanValidationPageComponent } from './human-validation/human-validation-page.component';
import { AboutPageComponent } from './layout/about-page.component';
import { StatusPageComponent } from './layout/status-page.component';
import { MunicipalUploadsPageComponent } from './municipal-uploads/municipal-uploads-page.component';
import { NotificationsPageComponent } from './notifications/notifications-page.component';
import { OpsGovernancePageComponent } from './ops-governance/ops-governance-page.component';
import { ProcuradoriaPageComponent } from './procuradoria/procuradoria-page.component';
import { SectoralEnrichmentPageComponent } from './sectoral-enrichment/sectoral-enrichment-page.component';
import { SourcesPageComponent } from './sources/sources-page.component';
import { TaxBetterAdminPageComponent } from './tax-better/tax-better-admin-page.component';
import { TaxBetterIntegrationPageComponent } from './tax-better/tax-better-integration-page.component';
import { TaxBetterVisionPageComponent } from './tax-better/tax-better-vision-page.component';
import { StateTransfersPageComponent } from './state-transfers/state-transfers-page.component';
import { TransferReconciliationPageComponent } from './transfer-reconciliation/transfer-reconciliation-page.component';
import { ValidationPageComponent } from './validation/validation-page.component';

const executive = 'Referência publicada';
const recovery = 'Referência publicada';
const transfers = 'Referência publicada';
const intelligence = 'Referência publicada';
const reform = 'Referência publicada';
const governance = 'Referência publicada';
const integration = 'Integração';
const vision = 'Visão';
const administration = 'Administração';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'visao' },
  {
    path: 'visao',
    component: TaxBetterVisionPageComponent,
    data: { title: 'Visão geral', group: vision },
  },
  {
    path: 'integracao',
    component: TaxBetterIntegrationPageComponent,
    data: { title: 'Entrada e saída', group: integration },
  },
  {
    path: 'entrar',
    component: LoginPageComponent,
    data: { title: 'Entrar', group: administration },
  },
  {
    path: 'administracao',
    component: TaxBetterAdminPageComponent,
    data: { title: 'Usuários e acessos', group: administration },
  },
  {
    path: 'executivo',
    component: DashboardPageComponent,
    data: { dashboardId: 'executivo', title: 'Visão executiva', group: executive },
  },
  {
    path: 'financeiro',
    component: DashboardPageComponent,
    data: { dashboardId: 'financeiro', title: 'Dinheiro do Município', group: executive },
  },
  {
    path: 'economia',
    component: DashboardPageComponent,
    data: { dashboardId: 'economia', title: 'Economia', group: intelligence },
  },
  {
    path: 'operacao',
    component: DashboardPageComponent,
    data: { dashboardId: 'operacao', title: 'Painel de operação', group: governance },
  },
  {
    path: 'achados',
    component: DashboardPageComponent,
    data: { dashboardId: 'achados', title: 'Achados', group: recovery },
  },
  {
    path: 'cobranca',
    component: DashboardPageComponent,
    data: { dashboardId: 'cobranca', title: 'Cobrança', group: recovery },
  },
  {
    path: 'pagamentos',
    component: DashboardPageComponent,
    data: { dashboardId: 'pagamentos', title: 'Pagamentos e parcelamentos', group: recovery },
  },
  {
    path: 'divida-ativa',
    component: DashboardPageComponent,
    data: { dashboardId: 'divida-ativa', title: 'Dívida ativa', group: recovery },
  },
  {
    path: 'transferencias',
    component: DashboardPageComponent,
    data: { dashboardId: 'transferencias', title: 'Transferências federais', group: transfers },
  },
  {
    path: 'ibs-cbs',
    component: DashboardPageComponent,
    data: { dashboardId: 'ibs-cbs', title: 'IBS/CBS', group: reform },
  },
  {
    path: 'qualidade',
    component: DashboardPageComponent,
    data: { dashboardId: 'qualidade', title: 'Qualidade e lineage', group: intelligence },
  },
  {
    path: 'auditoria',
    component: DashboardPageComponent,
    data: { dashboardId: 'auditoria', title: 'Auditoria', group: intelligence },
  },
  {
    path: 'gates',
    component: DashboardPageComponent,
    data: { dashboardId: 'gates', title: 'Gates', group: governance },
  },
  {
    path: 'publico',
    component: DashboardPageComponent,
    data: { dashboardId: 'publico', title: 'Painel público', group: executive },
  },
  {
    path: 'prontidao',
    component: DashboardPageComponent,
    data: { dashboardId: 'prontidao', title: 'Prontidão', group: reform },
  },
  {
    path: 'validacao',
    component: ValidationPageComponent,
    data: { title: 'Créditos e validação', group: recovery },
  },
  {
    path: 'validacao-humana',
    component: HumanValidationPageComponent,
    data: { title: 'Validação humana', group: governance },
  },
  {
    path: 'notificacoes',
    component: NotificationsPageComponent,
    data: { title: 'Alertas e metas', group: executive },
  },
  { path: 'funil', component: FunnelPageComponent, data: { title: 'Funil de recuperação', group: executive } },
  { path: 'calendario', component: CalendarPageComponent, data: { title: 'Calendário', group: reform } },
  {
    path: 'diagnostico',
    component: DiagnosisPageComponent,
    data: { title: 'Diagnóstico', group: governance },
  },
  {
    path: 'regras-auditoria',
    component: AuditRulesPageComponent,
    data: { title: 'Regras de auditoria', group: intelligence },
  },
  {
    path: 'casos-auditoria',
    component: AuditCasesPageComponent,
    data: { title: 'Casos de auditoria', group: recovery },
  },
  { path: 'fontes', component: SourcesPageComponent, data: { title: 'Fontes', group: intelligence } },
  {
    path: 'operacao-governanca',
    component: OpsGovernancePageComponent,
    data: { title: 'Operação e auditoria técnica', group: governance },
  },
  {
    path: 'upload-municipal',
    component: MunicipalUploadsPageComponent,
    data: { title: 'Upload municipal', group: governance },
  },
  {
    path: 'cadastro-360',
    component: Cadastro360PageComponent,
    data: { title: 'Cadastro 360', group: intelligence },
  },
  {
    path: 'setorial',
    component: SectoralEnrichmentPageComponent,
    data: { title: 'Inteligência Setorial', group: intelligence },
  },
  {
    path: 'transferencias-estaduais',
    component: StateTransfersPageComponent,
    data: { title: 'ICMS/IPVA estadual', group: transfers },
  },
  {
    path: 'conciliacao-transferencias',
    component: TransferReconciliationPageComponent,
    data: { title: 'Conciliação', group: transfers },
  },
  {
    path: 'procuradoria',
    component: ProcuradoriaPageComponent,
    data: { title: 'Procuradoria', group: recovery },
  },
  {
    path: 'saude',
    component: HealthPageComponent,
    data: { title: 'Saúde da plataforma', group: governance },
  },
  { path: 'sobre', component: AboutPageComponent, data: { title: 'Sobre', group: governance } },
  {
    path: 'erro',
    component: StatusPageComponent,
    data: {
      code: '500',
      title: 'Falha ao apresentar a página',
      message: 'A interface não completou esta leitura. Tente novamente. Nenhum dado foi inventado.',
      group: governance,
    },
  },
  {
    path: 'indisponivel',
    component: StatusPageComponent,
    data: {
      code: '503',
      title: 'Serviço temporariamente indisponível',
      message: 'A plataforma não confirmou disponibilidade. Aguarde e tente de novo, sem repetir carga.',
      group: governance,
    },
  },
  {
    path: '**',
    component: StatusPageComponent,
    data: {
      code: '404',
      title: 'Página não encontrada',
      message: 'O endereço não corresponde a um módulo do SIRTA.',
      group: governance,
    },
  },
];
