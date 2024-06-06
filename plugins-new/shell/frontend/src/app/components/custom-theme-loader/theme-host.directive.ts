import { Directive, ViewContainerRef } from '@angular/core';

@Directive({
  selector: '[themeHost]',
})
export class ThemeHost {
  constructor(public viewContainerRef: ViewContainerRef) {
  }
}
