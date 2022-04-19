import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AjentiConfiguration } from './ajenti-configuration.model';
import { GlobalConstantsService } from '../global-constants/global-contants.service';
import { AuthenticationProvider } from './authentication-provider.type';
import { Permission } from './permission.type';


/**
 * Provides functionalities to access/manage the Ajenti configurations.
 */
@Injectable({
  providedIn: 'root',
})
export class ConfigService {

  public config: AjentiConfiguration | null;

  constructor(
    private httpClient: HttpClient,
    private globalConstantsService: GlobalConstantsService,
  ) {
    this.config = globalConstantsService.constants.initialConfigContent;
  }

  /**
   * Loads the current config.
   */
  public async load(): Promise<void> {
    this.config = await this.httpClient
      .get<AjentiConfiguration>('/api/core/config')
      .toPromise() || null;
  }

  /**
   * Saves the current config.
   */
  public async save(): Promise<void> {
    await this.httpClient.post('/api/core/config', this.config);
  }

  /**
   * Gets the authentication providers.
   *
   * @param config The config to get the providers for.
   *
   * @returns A promise for the authentication providers.
   */
  public getAuthenticationProviders<T>(config: T): Promise<AuthenticationProvider[] | undefined> {
    return this.httpClient
      .get<AuthenticationProvider[]>('/api/core/authentication-providers', config)
      .toPromise();
  }

  /**
   * Gets the permissions.
   *
   * @param config The config to get the permissions for.
   *
   * @returns A promise for the permissions.
   */
  public getPermissions<T>(config: T): Promise<Permission[] | undefined> {
    return this.httpClient
      .get<Permission[]>('/api/core/permissions', config)
      .toPromise();
  }

}
