import { BehaviorSubject, Observable, lastValueFrom } from 'rxjs';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FileSystem } from '../view/fstab/filesystem.type';

@Injectable({
  providedIn: 'root'
})
export class FstabService {
  private _mounts: BehaviorSubject<FileSystem[]>;

  constructor(
    private httpClient: HttpClient,
  ) {
    this._mounts = new BehaviorSubject<FileSystem[]>([]);
  }

  get mounts(): Observable<FileSystem[]> {
    return this._mounts.asObservable();
  }

  public async loadMounts(): Promise<void> {
    const mount = await lastValueFrom(await this.httpClient.get<FileSystem[]>('/api/fstab/mounts'));
    this._mounts.next(mount);
  };

  public async umount(entry:FileSystem): Promise<void> {
      const resp = await lastValueFrom(this.httpClient.post<boolean>('/api/fstab/command_umount', {mountpoint: entry.mountpoint}));
      if (resp) {
        const mounts = this._mounts.value;
        const position = mounts.indexOf(entry);
        mounts.splice(position, 1);
        this._mounts.next(mounts);
      }
  }
}
