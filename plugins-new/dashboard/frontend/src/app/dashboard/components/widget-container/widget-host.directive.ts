import { Directive, ViewContainerRef } from '@angular/core';

@Directive({
  selector: '[widgetHost]',
})
export class WidgetHost {
  constructor(public viewContainerRef: ViewContainerRef) {
  }
}
