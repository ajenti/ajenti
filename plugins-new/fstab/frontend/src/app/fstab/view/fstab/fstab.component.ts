import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FileSystem } from './filesystem.type';
import { Devices, Fstab } from './devices.type';
import { NotificationService, TranslateService } from '@ngx-ajenti/core';
import { lastValueFrom } from 'rxjs';

@Component({
  selector: 'app-fstab',
  templateUrl: './fstab.component.html',
  //styleUrls: [ '../style.less' ],
})
export class FstabComponent {

  mounts: Array<FileSystem> = [];
  fstab: Fstab = {filesystems: []};
  devices: Array<Devices> = [];
  showDetails: boolean;


  constructor (
    private httpClient: HttpClient,
    private translate: TranslateService,
    private notify: NotificationService,
  ) {
    this.loadMounts();
    this.loadFstab();
    this.showDetails = false;
  };

  public async loadMounts(): Promise<void> {
    await lastValueFrom(this.httpClient.get<FileSystem[]>('/api/fstab/mounts')).then((filesystems) => {
      this.mounts = filesystems;
    }, () => {
      console.error('ERROR');
    });
  };

  public async umount(entry:FileSystem): Promise<void> {
    await lastValueFrom(this.httpClient.post('/api/fstab/command_umount', {mountpoint: entry.mountpoint})).then((resp) => {
            this.notify.success('', 'Device successfully unmounted!');
            let position = this.mounts.indexOf(entry);
            this.mounts.splice(position, 1);
        });;
  };

  public async loadFstab(): Promise<void> {
    await lastValueFrom(this.httpClient.get<Fstab>('/api/fstab')).then( (fstab) => {
	    this.fstab = fstab;
      this.devices = this.fstab.filesystems;
      console.log(this.fstab.filesystems);
    }, () => {
      console.error('ERROR');
    });
  };

    //   OLD CODE
    //   public async edit(device) => {
    //     $scope.edit_device = device;
    //     $scope.showDetails = true;
    // }
    //
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
