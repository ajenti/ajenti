import { PluginConfiguration } from './plugin-configuration';

export type AjentiUserConfiguration<T = PluginConfiguration> = {
  [pluginId: string]: T;
};
