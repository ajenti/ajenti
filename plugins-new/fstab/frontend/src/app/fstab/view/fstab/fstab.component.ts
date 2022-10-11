import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FileSystem } from './filesystem.type';
import { Devices, Fstab } from './devices.type';
import { NotificationService, TranslateService } from '@ngx-ajenti/core';
import { lastValueFrom } from 'rxjs';
import { FstabDialogComponent } from '../fstab-dialog/fstab-dialog.component';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';

@Component({
  selector: 'app-fstab',
  templateUrl: './fstab.component.html',
  //styleUrls: [ '../style.less' ],
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
    private dialog: MatDialog,
  ) {
    this.loadMounts();
    this.loadFstab();
    this.showDetails = false;
  };

  public async loadMounts(): Promise<void> {
    try {
      this.mounts = await lastValueFrom(this.httpClient.get<FileSystem[]>('/api/fstab/mounts'))
    } catch (error) {
      // error of type unknown, must be converted or be handled at top level
      this.notify.error('', 'message');
    };
  };

  public async umount(entry:FileSystem): Promise<void> {
    try {
      let resp = await lastValueFrom(this.httpClient.post('/api/fstab/command_umount', {mountpoint: entry.mountpoint}));
      this.notify.success('', this.translate.instant('Device successfully unmounted!'));
      let position = this.mounts.indexOf(entry);
      this.mounts.splice(position, 1);
    } catch (error) {
      // error of type unknown, must be converted or be handled at top level
      this.notify.error('', 'error');
    };
  };

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
    console.log(this.translate.instant('Edit'), device);
    let config = new MatDialogConfig();
    config.autoFocus = true;
    config.data = device;

    let dialogRef = this.dialog.open(FstabDialogComponent, config);
  };

  public remove(device: Devices): void {
    console.log('Remove', device);
  };

  public add(): void {
    console.log('Add');
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
