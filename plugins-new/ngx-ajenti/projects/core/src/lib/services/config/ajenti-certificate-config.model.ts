export class AjentiCertificateConfig {

  constructor(sslConfigResponse: any) {
    this.digest = sslConfigResponse.digest;
    this.name = sslConfigResponse.name;
    this.serial = sslConfigResponse.serial;
    this.user = sslConfigResponse.user;
  }

  public digest: string;
  public name: string;
  public serial: number;
  public user: string;

}
