import { Component } from '@angular/core';
import { WidgetComponent } from '../widget.component';
import { InputValidator } from '@ajenti/core/input-validator';

@Component({
  selector: 'app-uptime-widget',
  templateUrl: './uptime-widget.component.html',
  styleUrls: [ '../widget-shared.less' ],
})
export class UptimeWidgetComponent extends WidgetComponent {

  uptime: number = 0;

  constructor() {
    super(null);
  }
  
  updateWidgetWithNewValues(data: any): void {
    InputValidator.ensureIsNumber(data);
    this.uptime = data;
  }
}
