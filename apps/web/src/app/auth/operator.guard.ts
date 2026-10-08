import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { PublicOpenSessionService } from './public-open-session.service';

export const operatorGuard: CanActivateFn = () => {
  const session = inject(PublicOpenSessionService);
  if (session.peek()?.mode === 'OPERATOR_LOGIN') {
    return true;
  }
  return inject(Router).createUrlTree(['/entrar']);
};

export const loginGuard: CanActivateFn = () => {
  const session = inject(PublicOpenSessionService);
  if (session.peek()?.mode === 'OPERATOR_LOGIN') {
    return inject(Router).createUrlTree(['/visao']);
  }
  return true;
};
