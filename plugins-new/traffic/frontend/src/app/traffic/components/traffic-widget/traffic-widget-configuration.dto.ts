import { WidgetConfigurationDto } from '@ajenti-dashboard/models/user-config-service/widget-configuration.dto';

export class TrafficWidgetConfigurationDto extends WidgetConfigurationDto {
  
  constructor(public selectedInterface: string) {
    super();
  }
}
