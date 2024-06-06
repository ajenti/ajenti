import { Component } from '@angular/core';
import { WidgetComponent } from '../widget.component';
import { InputValidator } from '@ajenti/core/input-validator';

@Component({
  selector: 'app-loadavg-widget',
  templateUrl: './loadavg-widget.component.html',
  styleUrls: [ '../widget-shared.less' ],
})
export class LoadavgWidgetComponent extends WidgetComponent {

  averageLoad1minute: number = 0;
  averageLoad5minutes: number = 0;
  averageLoad15minutes: number = 0;

  constructor() {
    super(null);
  }

  updateWidgetWithNewValues(data: any): void {
    InputValidator.ensureInputIsNumberArray(data, 3);

    this.averageLoad1minute = data[0];
    this.averageLoad5minutes = data[1];
    this.averageLoad15minutes = data[2];
  }
}
