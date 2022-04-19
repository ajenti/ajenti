import { Component } from '@angular/core';
import { CdkDragDrop } from '@angular/cdk/drag-drop';
import { TabService } from '../../services/tab.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: [ '../../components/widget-shared.less' ],
})
export class DashboardComponent {

  constructor(
    public tabService: TabService,
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
}
