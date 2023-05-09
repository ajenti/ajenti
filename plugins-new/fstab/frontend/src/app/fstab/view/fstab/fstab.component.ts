import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FileSystem } from './filesystem.type';
import { Devices, Fstab } from './devices.type';
import { MessageBoxService, NotificationService, TranslateService } from '@ngx-ajenti/core';
import { lastValueFrom } from 'rxjs';
import { FstabService } from '../../services/fstab.service';
import { FstabDialogComponent } from '../../components/fstab-dialog/fstab-dialog.component';
import { MatButton } from '@angular/material/button';

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
  }

  // public async loadMounts(): Promise<void> {
  //   try {
  //     this.mounts = await lastValueFrom(this.httpClient.get<FileSystem[]>('/api/fstab/mounts'));console.log("load", this.mounts);
  //   } catch (error) {
  //     // error of type unknown, must be converted or be handled at top level
  //     this.notify.error('', 'message');
  //   };
  // };
  //
  // public async umount(entry:FileSystem): Promise<void> {
  //   try {
  //     console.log("before command:", this.mounts);
  //     let resp = await lastValueFrom(this.httpClient.post('/api/fstab/command_umount', {mountpoint: entry.mountpoint}));
  //     this.notify.success('', this.translate.instant('Device successfully unmounted!'));
  //     let position = this.mounts.indexOf(entry);console.warn("before splice:", this.mounts);
  //     this.mounts.splice(position, 1);
  //     // test
  //     this.mounts = [...this.mounts, this.mounts[1]];console.log(this.mounts);
  //   } catch (error) {
  //     // error of type unknown, must be converted or be handled at top level
  //     this.notify.error('', 'error');
  //   };
  //};

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
      title:"TEST",
      acceptButtonLabel:"OK",
      cancelButtonLabel:"Cancel",
      visible:true,
      injectedComponent: FstabDialogComponent,
      injectComponentData: device
    });
    messageBox.accepted = () => console.log('ACCEPTED');
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
