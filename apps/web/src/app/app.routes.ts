import { Routes } from '@angular/router';
import { ActiveDebtPageComponent } from './active-debt/active-debt-page.component';
import { AuditCasesPageComponent } from './audit-cases/audit-cases-page.component';
import { AuditRulesPageComponent } from './audit-rules/audit-rules-page.component';
import { Cadastro360PageComponent } from './cadastro-360/cadastro-360-page.component';
import { CalendarPageComponent } from './calendar/calendar-page.component';
import { CollectionPageComponent } from './collection/collection-page.component';
import { DashboardPageComponent } from './dashboard/dashboard-page.component';
import { DiagnosisPageComponent } from './diagnosis/diagnosis-page.component';
import { FindingsPageComponent } from './findings/findings-page.component';
import { FunnelPageComponent } from './funnel/funnel-page.component';
import { GatesPageComponent } from './gates/gates-page.component';
import { HealthPageComponent } from './health/health-page.component';
import { HumanValidationPageComponent } from './human-validation/human-validation-page.component';
import { MunicipalUploadsPageComponent } from './municipal-uploads/municipal-uploads-page.component';
import { NotificationsPageComponent } from './notifications/notifications-page.component';
import { OpsGovernancePageComponent } from './ops-governance/ops-governance-page.component';
import { PaymentsPageComponent } from './payments/payments-page.component';
import { PilotReadinessPageComponent } from './pilot-readiness/pilot-readiness-page.component';
import { ProcuradoriaPageComponent } from './procuradoria/procuradoria-page.component';
import { SourcesPageComponent } from './sources/sources-page.component';
import { TransferReconciliationPageComponent } from './transfer-reconciliation/transfer-reconciliation-page.component';
import { ValidationPageComponent } from './validation/validation-page.component';

export const routes: Routes = [
  { path: '', component: HealthPageComponent },
  { path: 'validacao', component: ValidationPageComponent },
  { path: 'validacao-humana', component: HumanValidationPageComponent },
  { path: 'notificacoes', component: NotificationsPageComponent },
  { path: 'cobranca', component: CollectionPageComponent },
  { path: 'pagamentos', component: PaymentsPageComponent },
  { path: 'divida-ativa', component: ActiveDebtPageComponent },
  { path: 'procuradoria', component: ProcuradoriaPageComponent },
  { path: 'funil', component: FunnelPageComponent },
  { path: 'calendario', component: CalendarPageComponent },
  { path: 'diagnostico', component: DiagnosisPageComponent },
  { path: 'regras-auditoria', component: AuditRulesPageComponent },
  { path: 'casos-auditoria', component: AuditCasesPageComponent },
  { path: 'fontes', component: SourcesPageComponent },
  { path: 'gates', component: GatesPageComponent },
  { path: 'operacao-governanca', component: OpsGovernancePageComponent },
  { path: 'upload-municipal', component: MunicipalUploadsPageComponent },
  { path: 'cadastro-360', component: Cadastro360PageComponent },
  { path: 'executivo', component: DashboardPageComponent, data: { dashboardId: 'executivo' } },
  { path: 'financeiro', component: DashboardPageComponent, data: { dashboardId: 'financeiro' } },
  { path: 'economia', component: DashboardPageComponent, data: { dashboardId: 'economia' } },
  { path: 'operacao', component: DashboardPageComponent, data: { dashboardId: 'operacao' } },
  { path: 'achados', component: FindingsPageComponent },
  { path: 'transferencias', component: DashboardPageComponent, data: { dashboardId: 'transferencias' } },
  {
    path: 'conciliacao-transferencias',
    component: TransferReconciliationPageComponent,
  },
  { path: 'ibs-cbs', component: DashboardPageComponent, data: { dashboardId: 'ibs-cbs' } },
  { path: 'qualidade', component: DashboardPageComponent, data: { dashboardId: 'qualidade' } },
  { path: 'auditoria', component: DashboardPageComponent, data: { dashboardId: 'auditoria' } },
  { path: 'publico', component: DashboardPageComponent, data: { dashboardId: 'publico' } },
  { path: 'prontidao', component: PilotReadinessPageComponent },
  { path: '**', redirectTo: '' },
];
