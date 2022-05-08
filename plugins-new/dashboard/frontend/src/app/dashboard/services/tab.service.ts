import { Injectable } from '@angular/core';
import { WidgetDto } from '../models/user-config-service/widget.dto';
import { DashboardConfigService } from './dashboard-config.service';
import { MessageBoxService, TranslateService } from '@ngx-ajenti/core';
import { DashboardConfigurationDto } from '../models/user-config-service/dashboard-configuration.dto';
import { TabDto } from '../models/user-config-service/tab.dto';

@Injectable({
  providedIn: 'root',
})
export class TabService {

  private _activeTabName: string = '';
  private _tabs: TabDto[] = [];
  private _activeWidgets: WidgetDto[] = [];

  get activeTabName(): string {
    return this._activeTabName;
  }

  get tabs(): TabDto[] {
    return this._tabs;
  }

  get activeWidgets(): WidgetDto[] {
    return this._activeWidgets;
  }

  constructor(
    private messageBoxService: MessageBoxService,
    private dashboardConfigService: DashboardConfigService,
    private translateService: TranslateService,
  ) {
    this.dashboardConfigService.getConfigUpdateListener().subscribe(
      (config: DashboardConfigurationDto) => this.onConfigChange(config));
  }

  onConfigChange(config: DashboardConfigurationDto): void {
    this._tabs = config.tabs;
    if (!this.activeTabName) {
      this.setActiveTab(config.tabs[0].name);
    }
  }

  addTab() {
    const messageBoxTitle = this.translateService.instant('New name');
    const acceptButtonLabel = this.translateService.instant('OK');
    const cancelButtonLabel = this.translateService.instant('Cancel');

    const messageBox = this.messageBoxService.show(undefined, undefined, messageBoxTitle,
      '', acceptButtonLabel, cancelButtonLabel);

    messageBox.accepted = () => {
      if (messageBox.value) {
        this.dashboardConfigService.addNewTab(messageBox.value);
      }
    };
  }

  renameTab() {
    const promptInitialValue = this.activeTabName;
    const promptTitle = this.translateService.instant('New name');
    const acceptButtonLabel = this.translateService.instant('OK');
    const cancelButtonLabel = this.translateService.instant('Cancel');

    const messageBox = this.messageBoxService.show(undefined, undefined, promptTitle,
      promptInitialValue, acceptButtonLabel, cancelButtonLabel);

    messageBox.accepted = () => {
      if (messageBox.value) {
        this.dashboardConfigService.renameTab(this.getIndexOfActiveTab(), messageBox.value);
      }
    };
  }

  deleteActiveTab() {
    if (!this.activeTabName) {
      return;
    }

    const indexTabToDelete = this.getIndexOfActiveTab();
    const messageboxTitle = this.translateService.instant('Remove the \'' + this.activeTabName + '\' tab?');
    const positiveButtonTitle = this.translateService.instant('Remove');
    const negativeButtonTitle = this.translateService.instant('Cancel');
    const messageBox = this.messageBoxService.show(messageboxTitle, undefined, undefined, undefined, positiveButtonTitle, negativeButtonTitle);
    messageBox.accepted = () => {
      this.setActiveTab(this._tabs[0].name);
￼     this.dashboardConfigService.removeTab(indexTabToDelete);
    };
  }

  setActiveTab(name: string) {
    this._activeTabName = name;
    this._activeWidgets = this.tabs[this.getIndexOfActiveTab()].widgets;
  }

  getIndexOfActiveTab(): number {
    return this.tabs.findIndex(tab => tab.name == this.activeTabName);
  }
}
