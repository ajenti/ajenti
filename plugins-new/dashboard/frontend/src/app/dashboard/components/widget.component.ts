import { Type } from '@angular/core';
import { WidgetConfigComponent } from './widget-config.component';
import { WidgetDto } from '../models/user-config-service/widget.dto';

export abstract class WidgetComponent {

  abstract updateWidgetWithNewValues(data: any): void;

  widget: WidgetDto = new WidgetDto();

  constructor(public configWidgetComponent: Type<WidgetConfigComponent> | null = null) {
  }
}
