import { AjentiClientAuthConfig } from './ajenti-client-auth-config.model';

export class AjentiSslConfig {

  constructor(sslConfigResponse: any) {
    this.certificate = sslConfigResponse.force;
    this.fqdnCertificate = sslConfigResponse.fqdn_certificate;
    this.clientAuth = new AjentiClientAuthConfig(sslConfigResponse.client_auth);
    this.enable = sslConfigResponse.enable;
  }

  public certificate: string;
  public fqdnCertificate: string;
  public clientAuth: AjentiClientAuthConfig;
  public enable: boolean;

}
