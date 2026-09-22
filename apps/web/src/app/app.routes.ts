import { Routes } from '@angular/router';
import { AuditCasesPageComponent } from './audit-cases/audit-cases-page.component';
import { AuditRulesPageComponent } from './audit-rules/audit-rules-page.component';
import { Cadastro360PageComponent } from './cadastro-360/cadastro-360-page.component';
import { CalendarPageComponent } from './calendar/calendar-page.component';
import { DashboardPageComponent } from './dashboard/dashboard-page.component';
import { DiagnosisPageComponent } from './diagnosis/diagnosis-page.component';
import { FunnelPageComponent } from './funnel/funnel-page.component';
import { HealthPageComponent } from './health/health-page.component';
import { HumanValidationPageComponent } from './human-validation/human-validation-page.component';
import { MunicipalUploadsPageComponent } from './municipal-uploads/municipal-uploads-page.component';
import { NotificationsPageComponent } from './notifications/notifications-page.component';
import { OpsGovernancePageComponent } from './ops-governance/ops-governance-page.component';
import { SectoralEnrichmentPageComponent } from './sectoral-enrichment/sectoral-enrichment-page.component';
import { SourcesPageComponent } from './sources/sources-page.component';
import { StateTransfersPageComponent } from './state-transfers/state-transfers-page.component';
import { TransferReconciliationPageComponent } from './transfer-reconciliation/transfer-reconciliation-page.component';
import { ValidationPageComponent } from './validation/validation-page.component';

/** Os 15 painéis oficiais compartilham DashboardPageComponent. */
const officialDashboards: Routes = [
  { path: 'executivo', component: DashboardPageComponent, data: { dashboardId: 'executivo' } },
  { path: 'financeiro', component: DashboardPageComponent, data: { dashboardId: 'financeiro' } },
  { path: 'economia', component: DashboardPageComponent, data: { dashboardId: 'economia' } },
  { path: 'operacao', component: DashboardPageComponent, data: { dashboardId: 'operacao' } },
  { path: 'achados', component: DashboardPageComponent, data: { dashboardId: 'achados' } },
  { path: 'cobranca', component: DashboardPageComponent, data: { dashboardId: 'cobranca' } },
  { path: 'pagamentos', component: DashboardPageComponent, data: { dashboardId: 'pagamentos' } },
  { path: 'divida-ativa', component: DashboardPageComponent, data: { dashboardId: 'divida-ativa' } },
  {
    path: 'transferencias',
    component: DashboardPageComponent,
    data: { dashboardId: 'transferencias' },
  },
  { path: 'ibs-cbs', component: DashboardPageComponent, data: { dashboardId: 'ibs-cbs' } },
  { path: 'qualidade', component: DashboardPageComponent, data: { dashboardId: 'qualidade' } },
  { path: 'auditoria', component: DashboardPageComponent, data: { dashboardId: 'auditoria' } },
  { path: 'gates', component: DashboardPageComponent, data: { dashboardId: 'gates' } },
  { path: 'publico', component: DashboardPageComponent, data: { dashboardId: 'publico' } },
  { path: 'prontidao', component: DashboardPageComponent, data: { dashboardId: 'prontidao' } },
];

export const routes: Routes = [
  { path: '', component: HealthPageComponent },
  ...officialDashboards,
  { path: 'validacao', component: ValidationPageComponent },
  { path: 'validacao-humana', component: HumanValidationPageComponent },
  { path: 'notificacoes', component: NotificationsPageComponent },
  { path: 'funil', component: FunnelPageComponent },
  { path: 'calendario', component: CalendarPageComponent },
  { path: 'diagnostico', component: DiagnosisPageComponent },
  { path: 'regras-auditoria', component: AuditRulesPageComponent },
  { path: 'casos-auditoria', component: AuditCasesPageComponent },
  { path: 'fontes', component: SourcesPageComponent },
  { path: 'operacao-governanca', component: OpsGovernancePageComponent },
  { path: 'upload-municipal', component: MunicipalUploadsPageComponent },
  { path: 'cadastro-360', component: Cadastro360PageComponent },
  { path: 'setorial', component: SectoralEnrichmentPageComponent },
  { path: 'transferencias-estaduais', component: StateTransfersPageComponent },
  {
    path: 'conciliacao-transferencias',
    component: TransferReconciliationPageComponent,
  },
  { path: '**', redirectTo: '' },
];
