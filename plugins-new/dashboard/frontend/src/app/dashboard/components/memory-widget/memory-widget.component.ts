import { Component } from '@angular/core';
import { WidgetComponent } from '../widget.component';

@Component({
  selector: 'app-memory-widget',
  templateUrl: './memory-widget.component.html',
  styleUrls: [ '../widget-shared.less' ],
})
export class MemoryWidgetComponent extends WidgetComponent {

  used: number = 0;
  total: number = 0;
  usage: number = 0;

  constructor() {
    super(null);
  }

  updateWidgetWithNewValues(data: any): void {
    if (!data) {
      throw Error('Invalid values for memory widget: ' + data);
    }

    this.used = data.used;
    this.total = data.total;
    this.usage = Math.floor((100 * this.used) / this.total);
  }
}
