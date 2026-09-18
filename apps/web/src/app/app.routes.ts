import { Routes } from '@angular/router';
import { CollectionPageComponent } from './collection/collection-page.component';
import { HealthPageComponent } from './health/health-page.component';
import { ValidationPageComponent } from './validation/validation-page.component';

export const routes: Routes = [
  { path: '', component: HealthPageComponent },
  { path: 'validacao', component: ValidationPageComponent },
  { path: 'cobranca', component: CollectionPageComponent },
  { path: '**', redirectTo: '' },
];
