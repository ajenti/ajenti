import { WidgetConfigurationDto } from './widget-configuration.dto';

export class WidgetDto {
  
  constructor(
    public typeId: string = '',
    public config: WidgetConfigurationDto = {},
    public id: string = WidgetDto.createWidgetId(typeId),
  ) {
  }

  private static createWidgetId(widgetTypeId: string): string {
    return 'widget-' + widgetTypeId + '-'
      + Date.now().toString(36) + Math.random().toString(36).substr(2);
  }
}
