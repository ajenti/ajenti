import { InjectionToken } from '@angular/core';

export const TOASTER_SERVICE_ADAPTER: InjectionToken<ToasterServiceAdapter> =
  new InjectionToken<ToasterServiceAdapter>('ToasterServiceToken');

export interface ToasterServiceAdapter {
  success(message?: string, title?: string): void;

  error(message?: string, title?: string): void;

  info(message?: string, title?: string): void;

  warning(message?: string, title?: string): void;
}
