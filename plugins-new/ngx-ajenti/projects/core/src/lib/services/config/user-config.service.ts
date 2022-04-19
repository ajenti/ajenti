import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { PluginConfiguration } from './plugin-configuration';
import { AjentiUserConfiguration } from './ajenti-user-configuration.type';


/**
 * Service responsible for loading and saving user configuration from/to the server.
 */
@Injectable({
  providedIn: 'root',
})
export class UserConfigService {

  private userConfig: { [pluginId: string]: BehaviorSubject<PluginConfiguration> };

  constructor(private httpClient: HttpClient) {
    this.userConfig = {};
    this.loadUserConfig();
  }

  getUserConfigListener<T>(pluginId: string): Observable<T | {}> {
    if (!this.userConfig[pluginId]) {
      this.userConfig[pluginId] = new BehaviorSubject<PluginConfiguration>({});
    }

    return this.userConfig[pluginId].asObservable();
  }

  loadUserConfig(): void {
    this.httpClient.get<AjentiUserConfiguration>('/api/core/user-config').subscribe(
      (userConfig: AjentiUserConfiguration) => {
        Object.keys(userConfig).forEach(pluginId => {
          this.updateUserConfig(pluginId, userConfig[pluginId]);
        });
      });
  }

  private updateUserConfig(pluginId: string, pluginConfiguration: PluginConfiguration) {
    if (!this.userConfig[pluginId]) {
      this.userConfig[pluginId] = new BehaviorSubject<PluginConfiguration>(pluginConfiguration);
    } else {
      this.userConfig[pluginId].next(pluginConfiguration);
    }
  }

  saveUserPluginConfiguration(pluginId: string, pluginConfiguration: PluginConfiguration): Observable<void> {
    this.updateUserConfig(pluginId, pluginConfiguration);
    const userConfigDto = this.convertUserConfigToDto();

    return this.httpClient.post<void>('/api/core/user-config', userConfigDto);
  }

  private convertUserConfigToDto(): AjentiUserConfiguration {
    const userConfig: AjentiUserConfiguration = {};
    Object.keys(this.userConfig).forEach(pluginId => {
      userConfig[pluginId] = this.userConfig[pluginId].value;
    });

    return userConfig;
  }
}
