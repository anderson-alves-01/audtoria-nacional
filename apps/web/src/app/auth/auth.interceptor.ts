import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { PublicOpenSessionService } from './public-open-session.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (
    req.url.startsWith('/health') ||
    req.url.includes('/v1/auth/public-open-session')
  ) {
    return next(req);
  }
  const session = inject(PublicOpenSessionService);
  const headers = session.authHeaders();
  if (!headers) {
    return next(req);
  }
  return next(req.clone({ setHeaders: headers }));
};
