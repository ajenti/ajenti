import { Injectable } from '@angular/core';
import { TabDto } from '../models/user-config-service/tab.dto';
import { UserConfigService } from '@ngx-ajenti/core';
import { DashboardConfigurationDto } from '../models/user-config-service/dashboard-configuration.dto';
import { WidgetComponentProvider } from './widget-component-provider';
import { WidgetTypeDto } from '../models/dashboard/widget-type-dto';
import { WidgetDto } from '../models/user-config-service/widget.dto';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class DashboardConfigService {
  private static readonly PLUGIN_ID = 'dashboard';
  private config: DashboardConfigurationDto = new DashboardConfigurationDto();
  private configUpdated: Subject<DashboardConfigurationDto> = new Subject<DashboardConfigurationDto>();


  getConfigUpdateListener(): Observable<DashboardConfigurationDto> {
    return this.configUpdated.asObservable();
  }

  constructor(
    private userConfigService: UserConfigService,
    private widgetComponentProvider: WidgetComponentProvider,
  ) {
    this.widgetComponentProvider.initializeWidgetComponents()
      .then(() => {
          this.subscribeToUserConfigChanges();
        },
      );
  }

  addNewTab(newTabName: string): void {
    this.config.tabs.push(new TabDto(newTabName, []));
    this.saveDashboardConfiguration();
  }

  renameTab(tabIndex: number, newName: string): void {
    this.config.tabs[tabIndex].name = newName;

    this.saveDashboardConfiguration();
  }

  removeTab(tabIndex: number): void {
    this.config.tabs.splice(tabIndex, 1);
    this.saveDashboardConfiguration();
  }

  addNewWidget(tabIndex: number, widgetType: WidgetTypeDto): void {
    const widget = new WidgetDto(widgetType.id);
    this.config.tabs[tabIndex].widgets.push(widget);
    this.saveDashboardConfiguration();
  }

  removeWidget(widgetToRemove: WidgetDto): void {
    for (const tab of this.config.tabs) {
      for (const widget of tab.widgets) {
        if (widgetToRemove.id == widget.id) {
          const indexOfWidgetToRemove = tab.widgets.indexOf(widget, 0);
          tab.widgets.splice(indexOfWidgetToRemove, 1);
        }
      }
    }

    this.saveDashboardConfiguration();
  }

  changeWidgetConfig(widgetId: string, configData: any): void {
    for (const tab of this.config.tabs) {
      for (const widget of tab.widgets) {
        if (widget.id == widgetId) {
          widget.config = configData;
        }
      }
    }

    this.saveDashboardConfiguration();
  }

  private subscribeToUserConfigChanges(): void {
    this.userConfigService
      .getUserConfigListener<DashboardConfigurationDto>(DashboardConfigService.PLUGIN_ID)
      .subscribe((config) => {
        let dashboardConfiguration = config as DashboardConfigurationDto;
        let hasAnyTabs = !!(dashboardConfiguration?.tabs?.length);
        if (!hasAnyTabs) {
          this.config = this.createDefaultConfiguration();
          this.configUpdated.next(this.config);
          this.saveDashboardConfiguration();
        } else {
          this.config = dashboardConfiguration;
          this.configUpdated.next(this.config);
        }
      });
  }

  private createDefaultConfiguration() {
    const defaultConfiguration = new DashboardConfigurationDto();
    defaultConfiguration.tabs.push(
      new TabDto('Home', [
        new WidgetDto('cpu'),
        new WidgetDto('uptime'),
      ]));

    return defaultConfiguration;
  }

  saveDashboardConfiguration(): void {
    this.userConfigService.saveUserPluginConfiguration(DashboardConfigService.PLUGIN_ID, this.config)
      .subscribe({
        error: (error) => console.error('Error while saving the plugin configuration:', error),
      });
  }
}
