import { Routes } from '@angular/router';
import { HealthPageComponent } from './health/health-page.component';

export const routes: Routes = [
  { path: '', component: HealthPageComponent },
  { path: '**', redirectTo: '' },
];
