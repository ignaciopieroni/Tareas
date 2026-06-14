import { ApplicationConfig, inject, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, Router, withViewTransitions } from '@angular/router';

import { routes } from './app.routes';
import { HTTP_INTERCEPTORS, provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideToastr, ToastrService } from 'ngx-toastr';
import { provideAnimations } from '@angular/platform-browser/animations';

import { AuthInterceptor } from './interceptors/auth-interceptor';
import { UserDataService } from './services/user-data-service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes, withViewTransitions()),

    /* Http-client con el interceptor y dependencias */
    provideHttpClient(withInterceptors([
      (req, next) => {
        const router = inject(Router);
        const toastr = inject(ToastrService);
        const interceptor = new AuthInterceptor(router, toastr);
        return interceptor.handle(req, next);
      }
    ])),
    provideToastr(),
    provideAnimations(),

    /* Interceptor de http queries para agregarles el header del jwt 
    {
      provide:HTTP_INTERCEPTORS,
      useClass:AuthInterceptor,
      multi:true
    }*/
  ]
};
