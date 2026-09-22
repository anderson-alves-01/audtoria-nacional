import { ApplicationConfig, APP_INITIALIZER, provideZoneChangeDetection } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';

import { authInterceptor } from './auth/auth.interceptor';
import { PublicOpenSessionService } from './auth/public-open-session.service';
import { routes } from './app.routes';

function bootstrapPublicOpenSession(session: PublicOpenSessionService) {
  return () =>
    session.ensureSession().catch(() => {
      // Dashboards will surface API errors; health remains public.
    });
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    {
      provide: APP_INITIALIZER,
      useFactory: bootstrapPublicOpenSession,
      deps: [PublicOpenSessionService],
      multi: true,
    },
  ],
};
