import { Routes } from '@angular/router';
import { CalendarPageComponent } from './calendar/calendar-page.component';
import { CollectionPageComponent } from './collection/collection-page.component';
import { FunnelPageComponent } from './funnel/funnel-page.component';
import { HealthPageComponent } from './health/health-page.component';
import { ValidationPageComponent } from './validation/validation-page.component';

export const routes: Routes = [
  { path: '', component: HealthPageComponent },
  { path: 'validacao', component: ValidationPageComponent },
  { path: 'cobranca', component: CollectionPageComponent },
  { path: 'funil', component: FunnelPageComponent },
  { path: 'calendario', component: CalendarPageComponent },
  { path: '**', redirectTo: '' },
];
