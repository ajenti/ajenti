import { Component } from '@angular/core';

import { DataInterface } from '@ngx-ajenti/core';

@Component({
  template: '',
})
export abstract class WidgetConfigComponent implements DataInterface {

  abstract getData(): any;

  abstract setData(data: any): void;
}
