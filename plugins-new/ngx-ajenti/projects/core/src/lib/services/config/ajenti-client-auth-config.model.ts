import { AjentiCertificateConfig } from './ajenti-certificate-config.model';

export class AjentiClientAuthConfig {

  constructor(sslConfigResponse: any) {
    this.enable = sslConfigResponse.enable;
    this.force = sslConfigResponse.force;
    this.certificates = sslConfigResponse.certificates
      ? sslConfigResponse.certificates.map((c: any) => new AjentiCertificateConfig(c))
      : [];
  }

  public enable: boolean;
  public force: boolean;
  public certificates: AjentiCertificateConfig[];

}
