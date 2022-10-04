export class Devices {

  constructor(item: Devices) {
    this.device = item.device;
    this.mountpoint = item.mountpoint;
    this.type = item.type;
    this.options = item.options;
    this.freq = item.freq;
    this.passno = item.passno;
  }

  public device: string;
  public mountpoint: string;
  public type: string;
  public options: string;
  public freq: string;
  public passno: string;

}

export class Fstab {

  constructor(item: Fstab) {
    this.filesystems = item.filesystems;
  }

  public filesystems: Array<Devices>;
}
