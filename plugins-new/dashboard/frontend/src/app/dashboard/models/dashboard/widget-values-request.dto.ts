import { WidgetConfigurationDto } from '../user-config-service/widget-configuration.dto';

export class WidgetValuesRequestDto {

  constructor(
    public widgetId: string,
    public widgetTypeId: string,
    public widgetConfig: WidgetConfigurationDto | null = null,
  ) {
    if (widgetConfig === null) {
      this.widgetConfig = {};
    }
  }
}
