import { Directive, ElementRef, Input } from '@angular/core';

@Directive({
  selector: '[autofocus]',
})
export class AutoFocusDirective {

  private focus = true;

  constructor(private el: ElementRef) {
  }

  ngAfterViewInit() {
    if (this.focus) {
      this.el.nativeElement.focus();
    }
  }

  @Input()
  public set autofocus(condition: boolean) {
    this.focus = condition !== false;
  }
}
