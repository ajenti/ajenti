import { Component, OnDestroy } from '@angular/core';
import { CdkDragDrop } from '@angular/cdk/drag-drop';
import { TabService } from '../../services/tab.service';
import { WidgetValuesService } from '../../services/widget-values.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: [ '../../components/widget-shared.less' ],
})
export class DashboardComponent implements OnDestroy {

  constructor(
    public tabService: TabService,
    private widgetValuesService: WidgetValuesService,
  ) {
  }

  drop(event: CdkDragDrop<any>) {
    if (!this.tabService.activeTabName) {
      return;
    }

    let currentTabWidgets = this.tabService.activeWidgets;
    currentTabWidgets[event.previousContainer.data.index] = event.container.data.item;
    currentTabWidgets[event.container.data.index] = event.previousContainer.data.item;
  }

  ngOnDestroy(): void {
    this.widgetValuesService.stopAutoUpdate();
  }
}
