import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FileSystem } from './filesystem.type';
import { Devices, Fstab } from './devices.type';
import { MessageBoxService, NotificationService, TranslateService } from '@ngx-ajenti/core';
import { lastValueFrom } from 'rxjs';
import { FstabService } from '../../services/fstab.service';
import { FstabDialogComponent } from '../../components/fstab-dialog/fstab-dialog.component';

@Component({
  selector: 'app-fstab',
  templateUrl: './fstab.component.html',
  styleUrls: [ './fstab.component.less' ],
})
export class FstabComponent {

  mounts: FileSystem[] = [];
  fstab: Fstab = {filesystems: []};
  devices: Devices[] = [];
  showDetails: boolean;

  constructor (
    private httpClient: HttpClient,
    private translate: TranslateService,
    private notify: NotificationService,
    private messageBoxService: MessageBoxService,
    private fstabService: FstabService,
  ) {
    this.fstabService.mounts.subscribe((mounts) => {
      this.mounts = mounts;
    });
    this.fstabService.loadMounts();
    this.loadFstab();
    this.showDetails = false;
  };

  public onUmountClick(entry:FileSystem): void {
    this.fstabService.umount(entry);
    this.notify.success('', entry.device + ' successfully unmounted');
  }

  public async loadFstab(): Promise<void> {
    try {
      this.fstab = await lastValueFrom(this.httpClient.get<Fstab>('/api/fstab'));
      this.devices = this.fstab.filesystems;
    } catch (error) {
      // error of type unknown, must be converted or be handled at top level
      this.notify.error('', 'error');
    };
  };

  public edit(device: Devices): void {
    const messageBox = this.messageBoxService.show({
      title:"Edit device",
      acceptButtonLabel:"Save",
      cancelButtonLabel:"Cancel",
      visible:true,
      injectedComponent: FstabDialogComponent,
      injectComponentData: device
    });
    messageBox.accepted = (updatedDevice) => {
      let position = this.devices.indexOf(device);
      this.devices[position] = <Devices>updatedDevice;
    };
  };

  public remove(device: Devices): void {
    const messageBox = this.messageBoxService.prompt("Do you really want to remove this device?");
    messageBox.accepted = (updatedDevice: Devices) => {
      let position = this.devices.indexOf(updatedDevice);
      this.devices.splice(position, 1);
    };
  };

  public add(): void {
    let device_new = <Devices>{};
    const messageBox = this.messageBoxService.show({
      title:"Add device",
      acceptButtonLabel:"Save",
      cancelButtonLabel:"Cancel",
      visible:true,
      injectedComponent: FstabDialogComponent,
      injectComponentData: device_new
    });
    messageBox.accepted = (updatedDevice) => {
      this.devices.push(<Devices>updatedDevice);
    };

  };

  private async save(): Promise<void> {
    let resp = await lastValueFrom(this.httpClient.post('/api/fstab', {config: this.fstab}));
    this.notify.success('', 'Fstab successfully saved!');
  };

    //   OLD CODE
    //   public async edit(device) => {
    //     $scope.edit_device = device;
    //     $scope.showDetails = true;
    // }
    //     $scope.remove = (device) => {
    //     messagebox.show({
    //         text: gettext('Do you really want to permanently delete this entry?'),
    //         positive: gettext('Delete'),
    //         negative: gettext('Cancel')
    //     }).then( () => {
    //         position = $scope.fstab.indexOf(device);
    //         $scope.fstab.splice(position, 1);
    //         $scope.save();
    //     })
    // }
    //
    //     $scope.add = () => {
    //     $scope.add_new = true;
    //     $scope.edit_device = {
    //         'device': '',
    //         'mountpoint': '/',
    //         'type': 'ext4',
    //         'options': 'defaults',
    //         'freq': '0',
    //         'passno': '0',
    //     };
    //     $scope.showDetails = true;
    // }
}
