import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { TrafficWidgetConfigComponent } from '../traffic-widget-config/traffic-widget-config.component';
import { WidgetComponent } from '@ajenti-dashboard/components/widget.component';
import { TrafficWidgetConfigurationDto } from './traffic-widget-configuration.dto';

@Component({
  selector: 'app-traffic-widget',
  templateUrl: './traffic-widget.component.html',
  styleUrls: [ '../widget-shared-link.less' ],
})

export class TrafficWidgetComponent extends WidgetComponent {

  selectedInterface = '';
  latestUpdateTimeStamp: number | null = null;
  bytesSentTotal = 0;
  bytesReceivedTotal = 0;
  bytesSentPerSecond = 0;
  bytesReceivedPerSecond = 0;

  constructor(public httpClient: HttpClient) {
    super(TrafficWidgetConfigComponent);
  }

  public updateWidgetWithNewValues(data: any) {
    if (!data) {
      return;
    }

    if (this.latestUpdateTimeStamp) {
      const secondsSinceLastUpdate = (Date.now() - this.latestUpdateTimeStamp) / 1000.0;
      const bytesSentSinceLastUpdate = data.bytesSent - this.bytesSentTotal;
      const bytesReceivedSinceLastUpdate = data.bytesReceived - this.bytesSentTotal;

      this.bytesSentPerSecond = bytesSentSinceLastUpdate / secondsSinceLastUpdate;
      this.bytesReceivedPerSecond = bytesReceivedSinceLastUpdate / secondsSinceLastUpdate;
    }

    this.latestUpdateTimeStamp = new Date().getTime();
    this.bytesSentTotal = data.bytesSent;
    this.bytesReceivedTotal = data.bytesReceived;
    this.selectedInterface = (this.widget.config as TrafficWidgetConfigurationDto)?.selectedInterface;
  }
}
