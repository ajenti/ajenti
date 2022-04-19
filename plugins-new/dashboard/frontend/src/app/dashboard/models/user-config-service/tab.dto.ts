import { WidgetDto } from './widget.dto';

export class TabDto {
  constructor(
    public name: string,
    public widgets: WidgetDto[],
  ) {
  }
}
