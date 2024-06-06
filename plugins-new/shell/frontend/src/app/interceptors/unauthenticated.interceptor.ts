import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { catchError, Observable } from 'rxjs';
import { Injectable, Injector } from '@angular/core';
import { IdentityService, MessageBoxService, NotificationService, TranslateService } from '@ngx-ajenti/core';
import { Router } from '@angular/router';
import { ServerErrorMessageComponent } from '@ajenti/components/server-error-message/server-error-message.component';

@Injectable()
export class UnauthenticatedInterceptor implements HttpInterceptor {

  private get identityService(): IdentityService {
    return this.injector.get(IdentityService);
  }

  private get translateService(): TranslateService {
    return this.injector.get(TranslateService);
  }

  private get notificationService(): NotificationService {
    return this.injector.get(NotificationService);
  }

  private get messageBoxService(): MessageBoxService {
    return this.injector.get(MessageBoxService);
  }

  private get router(): Router {
    return this.injector.get(Router);
  }

  // The interceptor loads the dependencies from the Injector to avoid cyclic dependencies.
  // (HttpClient -> HttpInterceptor -> IdentityService -> HttpClient)
  constructor(
    private injector: Injector,
  ) {
  }


  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

    return next.handle(request).pipe(
      catchError((error, src) => {

          const isSecurityError = error.status === 500 && error.error.exception === 'SecurityError';
          const isServerError = error.status === 500 && error.error.exception != 'EndpointError';
          const isUnauthorizedError = error.status === 401;

          if (isSecurityError) {
            this.handleSecurityError(error);
          } else if (isServerError) {
            this.handleServerError(error);
          } else if (isUnauthorizedError) {
            this.handleExpiredSession(error);
          }

          return next.handle(request);
        },
      ));
  }

  private handleServerError(error: any) {
    const messageBoxTitle = this.translateService.instant('Server error');
    const closeButtonText = this.translateService.instant('Close');
    const injectedComponentData = error;

    this.messageBoxService.show({
      title:messageBoxTitle,
      cancelButtonLabel: closeButtonText,
      visible:false,
      injectedComponent:ServerErrorMessageComponent,
      injectComponentData:injectedComponentData});
  }

  private handleExpiredSession(error: any): void {
    const isLoginViewOpen = this.router.url.includes('/view/login');
    if (isLoginViewOpen) {
      return;
    }

    const sessionExpiredText = this.translateService.instant('Your session has expired');
    this.notificationService.error(sessionExpiredText, '');
    const redirectPath = this.router.url;

    this.identityService.redirectToNormalLogin(redirectPath).then();
  }

  private handleSecurityError(error: any) {
    const securityErrorText = this.translateService.instant('Security error');
    this.notificationService.error(error.error.message, securityErrorText);
  }
}
