import { Type } from '@angular/core';

export interface MessageBoxParams<T = any> {
  text: string;
  title: string;
  promptText: string;
  promptInitialValue: string;
  acceptButtonLabel: string;
  cancelButtonLabel: string;
  visible: boolean;
  scrollable: boolean;
  progress: boolean;
  injectedComponent: Type<any>;
  injectComponentData: T;
}
