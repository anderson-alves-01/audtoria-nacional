import { Routes } from '@angular/router';
import { AuditRulesPageComponent } from './audit-rules/audit-rules-page.component';
import { CalendarPageComponent } from './calendar/calendar-page.component';
import { CollectionPageComponent } from './collection/collection-page.component';
import { DashboardPageComponent } from './dashboard/dashboard-page.component';
import { DiagnosisPageComponent } from './diagnosis/diagnosis-page.component';
import { FunnelPageComponent } from './funnel/funnel-page.component';
import { GatesPageComponent } from './gates/gates-page.component';
import { HealthPageComponent } from './health/health-page.component';
import { SourcesPageComponent } from './sources/sources-page.component';
import { ValidationPageComponent } from './validation/validation-page.component';

export const routes: Routes = [
  { path: '', component: HealthPageComponent },
  { path: 'validacao', component: ValidationPageComponent },
  { path: 'cobranca', component: CollectionPageComponent },
  { path: 'funil', component: FunnelPageComponent },
  { path: 'calendario', component: CalendarPageComponent },
  { path: 'diagnostico', component: DiagnosisPageComponent },
  { path: 'regras-auditoria', component: AuditRulesPageComponent },
  { path: 'fontes', component: SourcesPageComponent },
  { path: 'gates', component: GatesPageComponent },
  { path: 'executivo', component: DashboardPageComponent, data: { dashboardId: 'executivo' } },
  { path: 'financeiro', component: DashboardPageComponent, data: { dashboardId: 'financeiro' } },
  { path: 'economia', component: DashboardPageComponent, data: { dashboardId: 'economia' } },
  { path: 'operacao', component: DashboardPageComponent, data: { dashboardId: 'operacao' } },
  { path: 'achados', component: DashboardPageComponent, data: { dashboardId: 'achados' } },
  { path: 'pagamentos', component: DashboardPageComponent, data: { dashboardId: 'pagamentos' } },
  { path: 'divida-ativa', component: DashboardPageComponent, data: { dashboardId: 'divida-ativa' } },
  { path: 'transferencias', component: DashboardPageComponent, data: { dashboardId: 'transferencias' } },
  { path: 'ibs-cbs', component: DashboardPageComponent, data: { dashboardId: 'ibs-cbs' } },
  { path: 'qualidade', component: DashboardPageComponent, data: { dashboardId: 'qualidade' } },
  { path: 'auditoria', component: DashboardPageComponent, data: { dashboardId: 'auditoria' } },
  { path: 'publico', component: DashboardPageComponent, data: { dashboardId: 'publico' } },
  { path: 'prontidao', component: DashboardPageComponent, data: { dashboardId: 'prontidao' } },
  { path: '**', redirectTo: '' },
];
