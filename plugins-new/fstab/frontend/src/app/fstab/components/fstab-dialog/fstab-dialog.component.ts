import { Component } from '@angular/core';
import { DataInterface } from '@ngx-ajenti/core';
import { Devices } from '../../view/fstab/devices.type';

@Component({
  selector: 'fstab-dialog',
  templateUrl: './fstab-dialog.component.html',
  styleUrls: [ './fstab-dialog.component.less' ],
})
export class FstabDialogComponent implements DataInterface<Devices> {

  device: Devices | undefined;

  getData(): Devices {
    if (!this.device) {
      throw new Error("Device not defined");
    };
    return this.device;
  }

  setData(data: Devices): void {
    this.device = data;
  }

}
