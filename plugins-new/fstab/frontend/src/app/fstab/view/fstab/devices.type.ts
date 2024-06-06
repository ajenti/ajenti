export interface Devices {
  device: string;
  mountpoint: string;
  type: string;
  options: string;
  freq: string;
  passno: string;
}

export interface Fstab {
  filesystems: Array<Devices>;
}
