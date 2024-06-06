import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Injectable } from '@angular/core';
import { GlobalConstantsService } from '@ngx-ajenti/core';

@Injectable()
export class UrlPrefixInterceptor implements HttpInterceptor {

  constructor(
    private globalConstantsService: GlobalConstantsService,
  ) {
  }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (request.url && request.url[0] === '/') {
      const urlWithPrefix = this.globalConstantsService.constants.urlPrefix + request.url;
      request = request.clone({ url: urlWithPrefix });
    }

    return next.handle(request);
  }
}
