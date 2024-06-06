import { AjentiAuthConfig } from './ajenti-auth-config.model';
import { AjentiSslConfig } from './ajenti-ssl-config.model';

export class AjentiConfiguration {

  constructor(configResponse: any) {
    this.auth = new AjentiAuthConfig(configResponse.auth);
    this.color = configResponse.color;
    this.language = configResponse.language;
    this.maxSessions = configResponse.max_sessions;
    this.name = configResponse.name;
    this.restrictedUser = configResponse.restricted_user;
    this.sessionMaxTime = configResponse.session_max_time;
    this.ssl = new AjentiSslConfig(configResponse.ssl);
  }

  public auth?: AjentiAuthConfig;
  public color: string;
  public language: string;
  public maxSessions?: number;
  public name: string;
  public restrictedUser?: string;
  public sessionMaxTime?: number;
  public ssl?: AjentiSslConfig;

}
