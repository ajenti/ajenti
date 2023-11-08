import { WidgetConfigurationDto } from '@ajenti-dashboard/models/user-config-service/widget-configuration.dto';

export class WidgetTemplateConfigurationDto extends WidgetConfigurationDto {

  constructor(public selectedInterface: string) {
    super();
  }
}
