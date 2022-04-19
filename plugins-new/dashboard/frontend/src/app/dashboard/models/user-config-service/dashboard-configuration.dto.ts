import { TabDto } from './tab.dto';
import { PluginConfiguration } from '@ngx-ajenti/core';

export class DashboardConfigurationDto extends PluginConfiguration {
  tabs: TabDto[] = [];
}
