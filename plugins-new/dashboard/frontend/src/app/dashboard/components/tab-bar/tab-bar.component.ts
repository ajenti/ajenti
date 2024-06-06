import { Component, OnInit } from '@angular/core';
import { WidgetTypesService } from '../../services/widget-types.service';
import { DashboardConfigService } from '../../services/dashboard-config.service';
import { TabService } from '../../services/tab.service';

@Component({
  selector: 'app-tab-bar',
  templateUrl: './tab-bar.component.html',
})
export class TabBarComponent implements OnInit {

  constructor(
    public dashboardConfigService: DashboardConfigService,
    public widgetTypesService: WidgetTypesService,
    public tabService: TabService,
  ) {
  }

  ngOnInit(): void {
  }

}


