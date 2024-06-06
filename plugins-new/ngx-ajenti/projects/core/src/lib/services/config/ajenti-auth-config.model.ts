import { AjentiUser } from './ajenti-user.model';

export class AjentiAuthConfig {

  constructor(authConfigResponse: any) {
    this.allowSudo = authConfigResponse.allow_sudo;
    this.emails = authConfigResponse.emails;
    this.provider = authConfigResponse.provider;
    this.userConfig = authConfigResponse.user_config;
    this.users = authConfigResponse.users;
  }

  public allowSudo: boolean;
  public emails: string[];
  public provider: string;
  public userConfig: string;
  public users: { [username: string]: AjentiUser };

}
