import { Component } from '@angular/core';
import { DataInterface } from '@ngx-ajenti/core';
import { Devices } from '../../view/fstab/devices.type';

@Component({
  selector: 'fstab-dialog',
  templateUrl: './fstab-dialog.component.html',
  styleUrls: ['./fstab-dialog.component.less']
})
export class FstabDialogComponent implements DataInterface {

  device: Devices | undefined;

  constructor(
  ) { }

  getData(): Devices | undefined {
    return this.device;
  }

  setData(data: Devices): void {
    console.log(data);
    this.device = data;
  }


}
