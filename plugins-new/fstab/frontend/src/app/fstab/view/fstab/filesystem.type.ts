export class FileSystem {

  constructor(item: FileSystem) {
    this.device = item.device;
    this.mountpoint = item.mountpoint;
    this.used = item.used;
    this.size = item.size;
    this.usage = item.usage;
    this.fstype = item.fstype;
  }

  public device: string;
  public mountpoint: string;
  public used: number;
  public size: number;
  public usage: number;
  public fstype: string;

}
