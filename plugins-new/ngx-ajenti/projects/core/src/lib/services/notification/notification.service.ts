import { Inject, Injectable } from '@angular/core';
import { TOASTER_SERVICE_ADAPTER, ToasterServiceAdapter } from './toaster-service-adapter';

@Injectable({
  providedIn: 'root',
})
export class NotificationService {

  constructor(
    @Inject(TOASTER_SERVICE_ADAPTER) private toasterService: ToasterServiceAdapter,
  ) {
    if (!toasterService) {
      throw new Error('You must provide a toaster adapter');
    }
  }

  public info(title: string, text: string): void {
    this.toasterService.info(text, title);
  }

  public success(title: string, text: string): void {
    this.toasterService.success(text, title);
  }

  public warning(title: string, text: string): void {
    this.toasterService.warning(text, title);
  }

  public error(title: string, text: string): void {
    this.toasterService.error(text, title);
  }
}
