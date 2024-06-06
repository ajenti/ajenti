import { Component } from '@angular/core';
import { WidgetComponent } from '../widget.component';
import { InputValidator } from '@ajenti/core/input-validator';

@Component({
  selector: 'app-cpu-widget',
  templateUrl: './cpu-widget.component.html',
  styleUrls: [ '../widget-shared.less' ],
})

export class CpuWidgetComponent extends WidgetComponent {

  averageUsage: number = 0;
  activeCores: number = 0;
  averageUsageInPercents: number = 0;
  coresCount: number = 0;
  
  constructor() {
    super(null);
  }

  updateWidgetWithNewValues(data: any) {
    InputValidator.ensureInputIsNumberArray(data);

    const cpuUsagePerCore = data;// Example: [0.53, 0.86]
    this.averageUsage = 0;
    this.activeCores = 0;
    this.coresCount = cpuUsagePerCore.length;

    for (let i = 0; i < cpuUsagePerCore.length; i++) {
      const cpuUsageOfCurrentCore = cpuUsagePerCore[i];
      this.averageUsage += cpuUsageOfCurrentCore / cpuUsagePerCore.length;
      if (cpuUsageOfCurrentCore > 0) {
        this.activeCores += 1;
      }
    }

    this.averageUsageInPercents = Math.floor(this.averageUsage * 100);
  }
}
