import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
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
    private httpClient: HttpClient,
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
        console.log("In here ")
        const isDashboardConfigEmpty = Object.keys(config).length === 0;
        if (isDashboardConfigEmpty) {
          console.warn('No user defined dashboard found. Loading default dashboard ..');
          //TODO load default dashboard (customization service)
        } else {
          this.config = config as DashboardConfigurationDto;
          this.configUpdated.next(this.config);
        }
      });
  }

  saveDashboardConfiguration(): void {
    this.userConfigService.saveUserPluginConfiguration(DashboardConfigService.PLUGIN_ID, this.config)
      .subscribe({
        error: (error) => console.error('Error while saving the plugin configuration:', error),
      });
  }
}
