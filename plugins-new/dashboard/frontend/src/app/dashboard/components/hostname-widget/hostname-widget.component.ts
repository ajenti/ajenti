import { Component } from '@angular/core';
import { WidgetComponent } from '../widget.component';
import { InputValidator } from '@ajenti/core/input-validator';

@Component({
  selector: 'app-hostname-widget',
  templateUrl: './hostname-widget.component.html',
  styleUrls: [ '../widget-shared.less' ],
})

export class HostnameWidgetComponent extends WidgetComponent {

  hostname: string = '';

  constructor() {
    super(null);
  }

  updateWidgetWithNewValues(data: any): void {
    InputValidator.ensureIsString(data);

    this.hostname = data;
  }
}
