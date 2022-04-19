import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { WidgetConfigComponent } from '@ajenti-dashboard/components/widget-config.component';
import { DataInterface } from '@ngx-ajenti/core';

@Component({
  selector: 'app-traffic-widget-config',
  templateUrl: './traffic-widget-config.component.html',
  styleUrls: [ '../widget-shared-link.less' ],
})

export class TrafficWidgetConfigComponent extends WidgetConfigComponent implements OnInit, DataInterface {

  selectedInterface: string = '';
  interfaces: string[] = [];

  constructor(private httpClient: HttpClient) {
    super();
    this.selectedInterface = '';
  }

  setData(data: any): void {
    this.selectedInterface = data.interface;
  }

  getData(): any {
    return {
      interface: this.selectedInterface,
    };
  }

  ngOnInit(): void {
    this.initialize();
  }

  private initialize() {
    this.httpClient
      .get<string[]>
      ('/api/traffic/interfaces')
      .subscribe({
        next: (interfaces) => {
          this.interfaces = interfaces;
          if (!this.selectedInterface) {
            this.selectedInterface = this.interfaces[0];
          }
        },
        error: (error: any) => {
          console.error('Error retrieving interfaces for the Traffic widget.', error);
        },
      });
  }
}
