import { Component } from '@angular/core';
import { DataInterface } from '@ngx-ajenti/core';

@Component({
  selector: 'app-example-server-error-message',
  templateUrl: './server-error-message.component.html',
})

export class ServerErrorMessageComponent implements DataInterface {

  public message: any;

  constructor() {
  }

  getData(): any {
    return this.message;
  }

  setData(data: any): void {
    this.message = data;
  }
}
